from email import message
from pydoc import doc
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import logging # print function


# following set up from readme: https://github.com/nyu-software-engineering/flask-pymongo-web-app-example
app=Flask(__name__)

# PASTE CLUSTER FROM DISC HERE - it should work !!!!
cluster = MongoClient("mongodb+srv://team8:clothesclothesclothes@cluster0.5fub1c4.mongodb.net/?retryWrites=true&w=majority")

db = cluster["clothes-app"]

# collection for clothing 
clothing_collection = db["all-clothes"]
# collection for users
users = db["users"]
clothes = db["clothes"]
cart = db["cart"]


shirt1 = {
    "image" : "https://images.asos-media.com/products/adidas-originals-oversized-shirt-in-bliss-purple/202997913-1-purple?$n_640w$&wid=634&fit=constrain",
    "item-name" : "ADIDAS Oversized Shirt",
    "type" : "shirt",
    "price" : "60.00",
    "brand" : "adidas",
    "sizes-available" : ["m", "l"]
}

shirt2 = {
    "image" : "https://images.asos-media.com/products/ellesse-boyfriend-t-shirt-in-gray/200754513-1-grey?$n_320w$&wid=317&fit=constrain",
    "item-name" : "Ellesse Boyfriend T-Shirt in Gray",
    "price" : "31.00",
    "color": "gray",
    "brand" : "Ellesse",
    "sizes-available" : ["s", "m", "l" , "xl"]
}

pants1 = {
    "image" : "https://images.asos-media.com/products/yas-flared-pants-with-chunky-belt-loops-in-black/203019328-1-black?$n_640w$&wid=634&fit=constrain",
    "item-name" : "YAS Flared Pants",
    "price" : "79.00",
    "color": "black",
    "brand" : "YAS",
    "sizes-available" : ["s", "l", "xl"]
}

sweater1 = {
    "image" : "https://images.asos-media.com/products/topshop-knitted-textured-stripe-cardi-in-chocolate-and-pink/201993808-1-chocolatepik?$n_320w$&wid=317&fit=constrain",
    "item-name" : "Topshop knitted textured stripe cardigan",
    "price" : "67.00",
    "color": "chocolate",
    "brand" : "Topshop",
    "sizes-available" : ["s", "l"]
}

skirt1 = {
    "image" : "https://images.asos-media.com/products/style-cheat-satin-wrap-midi-skirt-in-pink-and-red-heart-print-part-of-a-set/201847163-1-pinkred?$n_320w$&wid=317&fit=constrain",
    "item-name" : "Style Cheat satin wrap midi skirt",
    "price" : "49.00",
    "color": "pink",
    "brand" : "Style Cheat",
    "sizes-available" : ["s", "l"]
}

skirt2 = {
    "image" : "https://images.asos-media.com/products/collusion-knit-skirt-in-jacquard/201055956-1-multi?$n_320w$&wid=317&fit=constrain",
    "item-name" : "COLLUSION knit skirt in jacquard",
    "price" : "46.90",
    "color": "brown",
    "brand" : "COLLUSION",
    "sizes-available" : ["s", "l"]
}





user0 = {
     'email': 'test@email.com',
    'username': 'test',
     'password': 'test123'    
}

# user has already been added 
# users.insert_one(user0)

# clothes added
# clothes.insert_many([shirt1, pants1, sweater1, skirt1])
# clothes.insert_one(shirt2)

# can't test, having errors with connecting to database the correct way -Eduarda
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

        if len(user_email) == 0:
            return render_template("signup.html", message="No Email")
        if len(user_name) == 0:
            return render_template("signup.html", message="No Name")
        if len(user_password) == 0:
            return render_template("signup.html", message="No Password")

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


@app.route("/")
@app.route("/login.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        # check credentials
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
            filterBy = request.form['filterList']
            if (filterBy == 'brand'):
                filteredClothing = db.clothes.find({'brand': 'Ellesse'})
            if (filterBy == 'color'):
                filteredClothing = db.clothes.find({'color': 'pink'})
            if (filterBy == 'size'):
                filteredClothing = db.clothes.find({'sizes-available': 's'})
            return render_template("list.html", clothes=filteredClothing)

        elif (request.form['sub'] == 'Search'):
            searchBy = request.form['toSearch'].lower()
            for doc in db.clothes.find(): 
                name = doc.get("item-name").lower()
                if (name.find(searchBy) != -1): 
                    db.clothes.update_one({"_id": doc.get("_id")}, {"$set":{"found":"1"}})
                else: 
                    db.clothes.update_one({"_id": doc.get("_id")}, {"$set":{"found":"0"}})
            return render_template("list.html", clothes=db.clothes.find({"found": "1"}))
    else:
        item = request.form["cart"]
        return redirect(url_for("cart.html"))

    



@app.route("/cart.html", methods = ['GET'])
def handle_item():
    if (request.args.get('item') == ""):
        displayCart = cart.find()
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
            return render_template("cart.html", clothes=displayCart)

@app.route("/edit.html", methods=['GET','POST'])
def edit():
    if request.method == "POST":
        id  = request.values.get("_id")
        user = users.find({"_id":ObjectId(id)})
        return render_template("edit.html", users=user, message ="Your changes are saved")
    else:
        return render_template("edit.html", message="")
    
@app.route("/payment.html")
def handle_confirmation(): 
    return render_template("payment.html")


@app.route('/delete.html')
def delete():
    id = request.values.get("_id")
    users.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    cart.delete_many({})
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(debug=True)