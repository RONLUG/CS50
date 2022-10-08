from cs50 import SQL
from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from utils import required_login
from consts import tags

app = Flask(__name__)
app.secret_key = "cf0d91a5c204a957c085f9fbca02e6ca2e904410acbc473c3d0c13bcc62aabe8"

db = SQL("sqlite:///app.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@required_login
@app.route("/")
def index():
    if session.get("username"):
        courses = db.execute("SELECT * FROM courses")
        return render_template("index.html", courses=courses)
    else:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        app.logger.info("%s", type(user))
        if len(user):
            user = user[0]
        else:
            return render_template("error.html", code=402, description="Invalid username or password")
        if not check_password_hash(user["password_hashed"], password):
            return render_template("error.html", code=402, description="Invalid username or password")
        else:
            session["username"] = username
            session["email"] = user["email"]
            return redirect("/")
    else:
        return render_template("login.html")


@app.route("/signin", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hashed = generate_password_hash(password)
        email = request.form.get("email")
        if username and password and email:
            existed = db.execute("SELECT * FROM users WHERE username=? OR email=?", username, email)
            if existed:
                return render_template("error.html", code=401, description="Username or Password had already taken")
            db.execute("INSERT INTO users (username, password_hashed, email) VALUES (?, ?, ?);", username, password_hashed, email)
            session["username"] = username
            session["email"] = email
            return redirect("/")
        else:
            return render_template("error.html", code=401, description="Enter username password and email.")
    else:
        return render_template("signin.html")


@app.route("/logout")
def logout():
    session["username"] = None
    session["email"] = None
    return redirect("/")


@required_login
@app.route("/create-course", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("description")
        tag = request.form.get("tag")
        id = db.execute("SELECT user_id FROM users WHERE username=?", session["username"])[0]["user_id"]
        app.logger.info("%i", id)
        if tag not in tags:
            return render_template("error.html", code=403, description="Invalid tag")
        db.execute("INSERT INTO courses (title, description, tag, publisher_id) VALUES (?, ?, ?, ?)", title, desc, tag, id)
        return redirect("/")
    else:
        return render_template("create-course.html", tags=tags)