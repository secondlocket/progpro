import os
import requests

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Book
from helpers import apology, login_required


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db.init_app(app)
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", code=403)
        elif not password:
            return apology("must provide password", code=403)

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.hash, password):
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

        user = User.query.filter_by(username=username).first()
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

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        input = request.form.get("input")
        search_key = f"%{input}%"

        isbn_query = None
        try:
            isbn_query = int(input)
        except ValueError:
            pass

        if isbn_query:  # If integer can look also for numbers in titles
            books = Book.query.filter(
                db.or_(
                    Book.isbn == isbn_query,
                    Book.title.ilike(search_key),
                    Book.author.ilike(search_key)
                )
            ).all()
        else:
            books = Book.query.filter(
                db.or_(
                    Book.title.ilike(search_key),
                    Book.author.ilike(search_key)
                )
            ).all()

        return render_template("search.html", books=books)
    return render_template("search.html")


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    if request.method == "POST":
        # post review
        return redirect("/")
    if request.method == "GET":

    return render_template("review.html")


@app.route("/book/<int:isbn>", methods=["GET"])
def book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return render_template(
            "apology.html",
            message="Book not found",
            code=404
        )

    value = book.isbn
    size = "M"
    cover = requests.get(f"https://covers.openlibrary.org/b/$ISBN/${value}-${size}.jpg?default=false")

    response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json")
    data = response.json()
    description = data[f"ISBN:{isbn}"]["details"]["description"]


    return render_template("book.html", book=book, cover=cover, description=description)

if __name__ == "__main__":
    app.run(debug=True)
