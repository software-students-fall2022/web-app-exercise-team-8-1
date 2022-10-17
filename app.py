from flask import Flask, render_template, request, redirect, abort, url_for, make_response
# following set up from readme: https://github.com/nyu-software-engineering/flask-pymongo-web-app-example

app=Flask(__name__)

# "localhost5000/" in browser
@app.route("/") 
def home():
    return "<h1> home <h1>"

if __name__ == "__main__":
    app.run(debug=True)