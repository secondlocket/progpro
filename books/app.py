import os

from flask import Flask, session, render_template
from flask_session import Session
from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def main():
    db.create_all()  # Create data table sql from database csv (from video)

# Routes
@app.route("/")
@login_required
def index():
    """Show books reviewed"""
    books = Book.query.all()
    portfolio = []

    for book in books:
        """print books out"""
        portfolio.append({
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "year": book.year
        })

    return render_template(
        "index.html",
        portfolio=portfolio,
        total_books=len(books)
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", code=403)
        elif not request.form.get("password"):
            return apology("must provide password", code=403)

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.hash, password)
            return apology("invalid username and/or password", 403)

        session["user_id"] = user.id

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")

        if not username:
            return apology("must provide username")
        if not password1:
            return apology("must provide password")
        if not password2:
            return apology("must confirm password")

        if password1 != password2:
            return apology("passwords do not match")

        user = Users.query.filter_by(username=username).first()
        if user:
            return apology("username already exists")

        hashedpw = generate_password_hash(password1)

        new_user = User(username=username, hash=hashedpw)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id

        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/search")
def search():
    if request.method == "POST":
        type == request.form.get("type")
        input == request.form.get("field")


    return render_template("search.html")

@app.route("/review", methods=["GET", "POST"])
def review():
    if request.method == "POST":
        # post review
        return redirect("/")
    if request.method == "GET":

    return render_template("review.html")

if __name__ == "__main__":
    with app.app_context():
        main()
    app.run(debug=True)
