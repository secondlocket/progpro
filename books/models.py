"""
Make Book class
"""

from flask_sqlalchemy import SQLAlchemy
from import import import


db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "books"
    # Search needs to access ISBN, title or author
    isbn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=True)
