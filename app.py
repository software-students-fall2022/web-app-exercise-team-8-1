from flask import Flask, render_template, request, session, redirect, url_for, make_response
from dotenv import dotenv_values
import pymongo
import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

config = dotenv_values(".env")


if config['FLASK_ENV'] == 'development':
    app.debug = True 

cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
db = cxn["database"]

users = db["users"]

@app. route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user_email = request.form["email"]
        user_name = request.form["username"]
        user_password = request.form["password"]

        if users.countDocuments({'email': user_email}) == 0:
            new_user = {
                'email': user_email,
                'username': user_name,
                'password': user_password
            }
            users.insert_one(new_user)

            return redirect(url_for("home"))
        else:
            render_template("login.html", message="User account already exists")
    else:
        return render_template("signup.html")


@app. route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        # check credentials
        x = users.findOne({'email': user_email})
        if x is not None:
            if x['password'] == user_password:

                return redirect(url_for("home"))
            else:
                return render_template("login.html", message="Wrong Password")
        else:
            return render_template("login.html", message="Invalid Email")

    else:
        return render_template("login.html", message="")



if __name__ == '__main__':
    app.run(debug=True)