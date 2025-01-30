from flask import Flask, request, redirect, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user

app = Flask(__name__)

#telling flask-sqlalchemy what database to connect to
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "falllback-secret-key")

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

#creating user model & database
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable = False)
    password = db.Column(db.string(250),
                         nullable=False)

db.init_app(app)
with app.app_context():
    db.create_all()

#adding a user loader: a function that flask-login can use to retrieve a user object given a user id

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

#functionality to register user of post request in made
@app.route('/register', methods= ["GET","POST"])
def register():
    if request.method == "POST":
        user = Users(users=request.form.get("username"),
                     password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect("login.html")
    return render_template("sign_up.html")

#functionality to login user
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.methos== "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user.password == request.form.get("password"):
            login_user(user)
            return render_template("login.html")

















    #credits: https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login/
    #credits: chatgpt