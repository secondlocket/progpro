import csv
import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import Book
from app import *

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open("books.csv", encoding="utf-8") as f:
        reader = csv.reader(f)

        next(reader)

        for isbn, title, author, year in reader:
            book = Book(isbn=isbn, title=title, author=author, year=year)
            db.add(book)
        db.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
