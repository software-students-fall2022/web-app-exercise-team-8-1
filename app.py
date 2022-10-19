import pymongo
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
# following set up from readme: https://github.com/nyu-software-engineering/flask-pymongo-web-app-example
app=Flask(__name__)

# PASTE CLUSTER FROM DISC HERE - it should work !!!!
cluster = MongoClient("mongodb+srv://team8:clothesclothesclothes@cluster0.5fub1c4.mongodb.net/?retryWrites=true&w=majority")

db = cluster["clothes-app"]

# collection for clothing 
clothing_collection = db["all-clothes"]
# collection for users
user_collection = db["users"]


clothes = db["clothes"]

shirt1 = {
    "image" : "https://images.asos-media.com/products/adidas-originals-oversized-shirt-in-bliss-purple/202997913-1-purple?$n_640w$&wid=634&fit=constrain",
    "item-name" : "Oversized Shirt",
    "type" : "shirt",
    "price" : "60.00",
    "brand" : "adidas",
    "sizes-available" : ["m", "l"]
}

pants1 = {
    "image" : "https://images.asos-media.com/products/yas-flared-pants-with-chunky-belt-loops-in-black/203019328-1-black?$n_640w$&wid=634&fit=constrain",
    "item-name" : "Flared Pants",
    "price" : "79.00",
    "color": "black",
    "brand" : "YAS",
    "sizes-available" : ["s", "l", "xl"]
}

user0 = {
     'email': 'test@email.com',
    'username': 'test',
     'password': 'test123'    
}

# users.insert_one(user0)

# clothes added
# clothes.insert_many([shirt1, pants1])

# can't test, having errors with connecting to database the correct way -Eduarda
@app.route("/list.html") 
def shop():
    #print(pymongo.version)
    #no filter requested, no GET or POST
    clothing = clothes.find()
    return render_template('list.html', clothes=clothing)

@app. route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user_email = request.form["email"]
        user_name = request.form["username"]
        user_password = request.form["password"]

        if user_collection.count_documents({'email': user_email}) == 0:
            new_user = {
                'email': user_email,
                'username': user_name,
                'password': user_password
            }
            user_collection.insert_one(new_user)

            return redirect(url_for("list"))
        else:
            render_template("login.html", message="User account already exists")
    else:
        return render_template("signup.html")


@app.route("/login.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        # check credentials
        x = user_collection.find_one({'email': user_email})
        if x is not None:
            if x['password'] == user_password:

                return redirect(url_for("list"))
            else:
                return render_template("login.html", message="Wrong Password")
        else:
            return render_template("login.html", message="Invalid Email")

    else:
        return render_template("login.html", message="")

@app.route("/list.html", methods=['POST'])
def handle_sort():
    sortBy = request.form['sortList']

    if (sortBy == 'default'): 
        sortedClothing =  db.clothes.find()
    elif (sortBy == 'name'):
        sortedClothing = db.clothes.find().sort('item-name',1)
    elif (sortBy == 'price'):
        sortedClothing = db.clothes.find().sort('price',1)
    elif (sortBy == 'brand'):
        sortedClothing = db.clothes.find().sort('brand',-1)
        
       

    return render_template("list.html", clothes=sortedClothing)


@app.route("/logout")
def logout():
    return render_template('login.html')
    

if __name__ == '__main__':
    app.run(debug=True)