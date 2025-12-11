import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

"""
TODO:
    /register (check no 400?)
    /quote (make quote.html and quoted.html)
    /buy (make buy.html)

    maak finance af voor het weekend
    maak books af voor volgende dinsdag

"""

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""
routes
"""
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    portfolio = []
    total_stocks_value = 0

    rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = rows[0]["cash"]

    stocks = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0
    """, user_id)

    for stock in stocks:
        dict = lookup(stock["symbol"])
        value = dict["price"] * stock["total_shares"]
        total_stocks_value += value

        portfolio.append({
            "symbol": stock["symbol"],
            "name": dict["name"],
            "shares": stock["total_shares"],
            "price": dict["price"],
            "total": value
        })

    grand_total = cash + total_stocks_value

    return render_template("index.html",
        portfolio=portfolio,
        cash=cash,
        grand_total=grand_total
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    """ TODO
    check not returning 400 and blank page """
    if request.method == "POST":
        """
        when form is submitted via POST,
        check for possible errors and insert
        the new user into users table
        """
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

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 0:
            return apology("username already exists :(")

        hashedpw = generate_password_hash(password1)
        new_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hashedpw
        )

        session["user_id"] = new_id
        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", code=403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", code=403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", code=403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """ TODO
    Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        dict = lookup(symbol)

        if dict is None:
            return apology("Invalid symbol")
        else:
            name = dict["name"]
            price = dict["price"]

            return render_template("quoted.html",
                name = name,
                price = usd(price),
                symbol = symbol
            )
    else:
        return render_template("quote.html")
    return apology("POST/GET niet aangeroepen bij quote")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        dict = lookup(symbol)

        # Checks
        if dict is None:
            return apology("must provide valid symbol")
        else:
            price = dict["price"]

        shares = int(shares)
        if shares <= 0:
            return apology("shares must be positive")

        total_cost = price * shares

        # Odds are you’ll want to SELECT how much cash
        # the user currently has in users. (cash variable name)
        user_id = session["user_id"]
        rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = rows[0]["cash"]

        if cash < total_cost:
            return apology("not enough credit")

        updated_cash = cash - total_cost

        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id, symbol.upper(), shares, price
        )
        return redirect("/")
    else:
        return render_template("buy.html")

    return apology("GET/POST niet aangeroepen bij buy")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        dict = lookup(symbol)

        if not symbol:
            return apology("must select stock")
        if not shares:
            return apology("must select shares")

        shares = int(shares)
        if dict is None:
            return apology("must provide valid symbol")
        if shares <= 0:
            return apology("shares must be positive")

        user_shares = db.execute("""
            SELECT SUM(shares) as total_shares
            FROM transactions
            WHERE user_id = ? AND symbol = ?
            GROUP BY symbol
            """,
            user_id,
            symbol
        )

        if not user_shares or user_shares[0]["total_shares"] <= 0:
            return apology("you don't own this stock")

        if shares > user_shares[0]["total_shares"]:
            return apology("not enough shares")

        if not dict:
            return apology("invalid symbol")

        price = dict["price"]
        total_profit = price * shares

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
            total_profit,
            user_id
        )
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
        user_id,
        symbol,
        -shares,
        price
    )

        return redirect("/")
    else:
        stocks = db.execute("""
            SELECT symbol
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(shares) > 0
            """, user_id
        )

        return render_template("sell.html", stocks=stocks)
    return apology("GET/POST niet aangeroepen bij sell")

@app.route("/history")
@login_required

def history():
    """Show history of transactions"""
    return apology("TODO")
