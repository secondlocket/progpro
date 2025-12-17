import csv
import os

from flask import Flask
from models import *

app = Flask(__name__)

# Database configuration
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def main():
    db.create_all()

    with open("books.csv") as f:
        reader = csv.reader(f)
        next(reader)

        for isbn, title, author, year in reader:
            book = Book(isbn=isbn, title=title, author=author, year=year)
            db.session.add(book)
            print(f"Added book {title}")
        db.session.commit()

    print("Done")

if __name__ == "__main__":
    with app.app_context():
        main()
