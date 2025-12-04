import os

from flask import Flask, session
from flask_session import Session
from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

def main():
    db.create_all()  # Create data table sql from database csv (from video)

@app.route("/")
def index():
    return "Project 1: TODO"

@app.route("/login")
def login():

@app.route("/logout")
def logout():

@app.route("/search")
def search():
    return render_template("search.html")


if __name__ == "__main__":
    with app.app_context():
        main()
