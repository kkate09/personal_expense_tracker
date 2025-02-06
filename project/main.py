from flask import Flask, request, redirect, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret-key")

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User Model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

# Expense Model
class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    description =  db.Column(db.String(250), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Category Model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)

# Budget Model
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    limit = db.Column(db.Integer, nullable=False)



# Create database tables
with app.app_context():
    db.create_all()


# manually inserting predefined categories
    predefined_categories = ["Food", "Transport", "Entertainment", "Bills", "Savings"]

    for category_name in predefined_categories:
        existing_category = Category.query.filter_by(name=category_name).first()
        if not existing_category:
            new_category = Category(name=category_name)
            db.session.add(new_category)

    db.session.commit()
    print("Categories added successfully!")


# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# User Registration Route
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(
            username=request.form.get("username"),
            password=request.form.get("password")
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("sign_up.html")

# User Login Route
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    expenses = db.session.query(
        Expenses.id,
        Expenses.date,
        Expenses.amount,
        Expenses.description,
        Category.name.label("category_name")
    ).join(Category, Expenses.category_id == Category.id).filter(Expenses.user_id == current_user.id).all()
    return render_template("dashboard.html", expenses=expenses)



@app.route("/add-expense", methods=["GET", "POST"])  # Allow both GET and POST
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form.get("amount")
        date = request.form.get("date")
        category_id = request.form.get("category")
        description = request.form.get("description")

        new_expense = Expenses(user_id=current_user.id, date=date, description=description, amount=amount, category_id=category_id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect("/dashboard")  # Redirect after saving

    # Fetch categories when rendering the form
    categories = Category.query.all()
    return render_template("new_expense.html", categories=categories)






# Home Page Route
@app.route("/")
def home():
    return render_template("home.html")




# Logout Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")  # Fixed redirection

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
