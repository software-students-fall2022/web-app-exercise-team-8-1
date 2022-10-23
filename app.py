from email import message
from pydoc import doc
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import logging # print function
import re

# following set up from readme: https://github.com/nyu-software-engineering/flask-pymongo-web-app-example
app=Flask(__name__)

# PASTE CLUSTER FROM DISC HERE - i1t should work !!!!
cluster = MongoClient("mongodb+srv://team8:clothesclothesclothes@cluster0.5fub1c4.mongodb.net/?retryWrites=true&w=majority")

db = cluster["clothes-app"]

# collection for clothing 
clothing_collection = db["all-clothes"]
# collection for users
users = db["users"]
clothes = db["clothes"]
cart = db["cart"]


user0 = {
     'email': 'test@email.com',
    'username': 'test',
     'password': 'test123'    
}

#clothes.delete_one({"item-name" :  "Urban Revivo denim shortsin mid wash denim"})
# user has already been added 
# users.insert_one(user0)
# clothes added
#clothes.insert_many([item1, item2, item3, item4])
#clothes.insert_one(item4)

@app.route("/list.html") 
def shop():
    #print(pymongo.version)
    clothing = clothes.find()
    return render_template('list.html', clothes=clothing)

@app.route("/signup.html", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user_email = request.form["email"]
        user_name = request.form["username"]
        user_password = request.form["password"]
        valid_email = "([A-Z]|[a-z]|[0-9])+@([a-z]|[A-Z])+\.(([a-z]){2}|([a-z]){3})"
        validation = re.match(valid_email, user_email)

        if len(user_email) == 0 or validation is None:
            return render_template("signup.html", message="Please enter valid email")
        if len(user_name) == 0:
            return render_template("signup.html", message="Please enter valid username")
        if len(user_password) == 0:
            return render_template("signup.html", message="Please enter valid password")

        if users.count_documents({'email': user_email}) == 0:
            new_user = {
                'email': user_email,
                'username': user_name,
                'password': user_password
            }
            users.insert_one(new_user)

            return redirect(url_for("handle_query"))
        else:
            return render_template("login.html", message="User account already exists")
    else:
        return render_template("signup.html")

# ---- TEST INFO 
# email : test@email.com
# username : test 
# pass : 1234
@app.route("/")
@app.route("/login.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        # check credentials
        valid_email = "([A-Z]|[a-z]|[0-9])+@([a-z]|[A-Z])+\.(([a-z]){2}|([a-z]){3})"
        validation = re.match(valid_email, user_email)

        if len(user_email) == 0 or validation is None:
            return render_template("login.html", message="Please enter valid email")
        if len(user_password) == 0:
            return render_template("login.html", message="Please enter valid Password")

        x = users.find_one({'email': user_email})
        if x is not None:
            if x['password'] == user_password:
                return redirect(url_for("handle_query"))
            else:
                return render_template("login.html", message="Wrong Password")
        else:
            return render_template("login.html", message="Invalid Email")

    else:
        return render_template("login.html", message="")

@app.route("/list.html", methods=['POST', 'GET'])
def handle_query():
    if request.method == "POST":
        if (request.form['sub'] == 'Display'):
            sortBy = request.form['sortList']
            if (sortBy == 'default'): 
                sortedClothing =  db.clothes.find()
            elif (sortBy == 'name'):
                sortedClothing = db.clothes.find().sort('item-name',1)
            elif (sortBy == 'price'):
                sortedClothing = db.clothes.find().sort('price',1)
            elif (sortBy == 'priceOpp'):
                sortedClothing = db.clothes.find().sort('price',-1)
            elif (sortBy == 'brand'):
                sortedClothing = db.clothes.find().sort('brand',-1)
            return render_template("list.html", clothes=sortedClothing)
            
        elif(request.form['sub'] == 'Filter'):
            brands = request.form.getlist('Brand')
            prices = request.form.getlist('price')
            sizes = request.form.getlist('size')
            results = db.clothes.find(
                {'brand': {'$in': brands},
                 'price': {'$lte': prices},
                 'sizes-available': {'$in': sizes}
                }
            )
            # return "<h1>Results" + str(results)+"</h1>"
            # return "<h5>brands: " + str(brands) + " prices: " + str(prices) + " sizes: " + str(sizes)+"</h5>"
            # for doc in db.clothes.find(
            #     {'brand': {'$in': brands},
            #      'price': {'$lte': prices},
            #      'sizes-available': {'$in': sizes}
            #     }):
            #     name = doc.get('item-name')
            #     if (name.find(searchBy) != -1): 
            #         db.clothes.update_one({"_id": doc.get("_id")}, {"$set":{"found":"1"}})
            #     else: 
            #         db.clothes.update_one({"_id": doc.get("_id")}, {"$set":{"found":"0"}})
                    
            # return render_template("list.html", clothes=db.clothes.find({"found": "1"}))                
            # return render_template("list.html", clothes=results)
        elif (request.form['sub'] == 'Search'):
            searchBy = request.form['toSearch'].lower()
            for doc in db.clothes.find(): 
                name = doc.get("item-name").lower()
                if (name.find(searchBy) != -1): 
                    db.clothes.update_one({"_id": doc.get("_id")}, {"$set":{"found":"1"}})
                else: 
                    db.clothes.update_one({"_id": doc.get("_id")}, {"$set":{"found":"0"}})
            return render_template("list.html", clothes=db.clothes.find({"found": "1"}))
  

    
@app.route("/item.html", methods = ['GET'])
def handle_view():
    id = request.args.get('item')
    if (id == ""):
        return "Oops! Looks like something went wrong."
    else:
        #cart.delete_many({})
        item = clothes.find_one({"_id": ObjectId(id)})
        return render_template("item.html", item=item)


@app.route("/cart.html", methods = ['GET'])
def handle_item():
    if (request.args.get('item') == ""):
        displayCart = cart.find_one()
        return render_template("cart.html", clothes=displayCart)
    else: 
        try: 
            id = request.args.get('item')
            found =  db.clothes.find_one({"_id" : ObjectId(id)})
            cart.insert_one(found)
        
        except:
            print("DO NOTHING")
        finally: 
            displayCart = cart.find()
            total = 0
            num = 0

            for item in displayCart:
                total += float(item["price"])
                num = num+1

            return render_template("cart.html", clothes=cart.find(), total = total, num = num)


@app.route('/account.html', methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        current_email = request.form["current_email"]
        current_password = request.form["current_password"]
        validate_current = users.find_one({'email': current_email})
        if validate_current is None:
            return render_template("account.html", message = "This account does not exist")
        if validate_current['password'] != current_password:
            return render_template("account.html", message = "Failed to validate password")

        user_id = validate_current['_id']

        user_email = request.form["email"]
        user_name = request.form["username"]
        user_password = request.form["password"]
        #input validation
        valid_email = "([A-Z]|[a-z]|[0-9])+@([a-z]|[A-Z])+\.(([a-z]){2}|([a-z]){3})"
        validation = re.match(valid_email, user_email)
        valid = False
        doc = {}

        if len(user_email) != 0 and validation is not None:
            doc["email"] = user_email
            valid = True
        if len(user_name) != 0:
            doc["username"] = user_name
            valid = True
        if len(user_password) != 0:
            doc["password"] = user_password
            valid = True

        if not valid:
            return render_template('account.html', message="Not valid update!")
        #end of input validation
        
        db.users.update_one({"_id": user_id},{ "$set": doc })
        return render_template("account.html")
    
    else:
        id = request.args.get('users')
        doc = db.users.find_one({"_id": ObjectId(id)})
        return render_template('account.html', doc=doc) # render the account template


@app.route("/cart.html", methods = ['Post'])
def edit_cart():
    try:
        cart_id = request.form["item"]
        cart.delete_one({"_id": ObjectId(cart_id)})
    except:
        return render_template("cart.html", message="deletion failed")
    finally:
        return redirect(url_for('edit_cart'))
    
@app.route("/payment.html", methods = ['GET'])
def handle_payment(): 
    total = request.args.get('total')
    numItems = request.args.get('num')
    return render_template("payment.html", total = total, numItems = numItems)

@app.route("/confirmation.html")
def handle_confirmation(): 
    return render_template("confirmation.html")


@app.route('/delete.html')
def delete():
    id = request.values.get("_id")
    users.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('login'))

@app.route("/logout.html")
def logout():
    cart.delete_many({})
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(debug=True)