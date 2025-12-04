"""
Provided for you in this project is a file called books.csv,
which is a spreadsheet in CSV format of 5000 different books.
Each one has an ISBN number, a title, an author, and a
publication year. In a Python file called import.py separate
from your web application, write a program that will take
the books and import them into your PostgreSQL database. You
will first need to decide what table(s) to create, what
columns those tables should have, and how they should relate
to one another. Run this program by running python3 import.py
to import the books into your database, and submit this program
with the rest of your project code.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "books"
    # Search needs to access ISBN, title or author
    isbn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=True)
