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

# TODO: fix required_login decorator
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
        if len(user):
            user = user[0]
        else:
            return render_template("error.html", code=402, description="Invalid username or password")
        if not check_password_hash(user["password_hashed"], password):
            return render_template("error.html", code=402, description="Invalid username or password")
        else:
            session["username"] = username
            session["email"] = user["email"]
            session["id"] = user["user_id"]
            return redirect("/")
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
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
            session["id"] = db.execute("SELECT * FROM users WHERE username = ?", username)["user_id"]
            return redirect("/")
        else:
            return render_template("error.html", code=401, description="Enter username password and email.")
    else:
        return render_template("signup.html")


@app.route("/logout")
def logout():
    session["username"] = None
    session["email"] = None
    session["id"] = None
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


@app.route("/your-courses", methods=["GET"])
def your_courses():
    enrolls = db.execute("SELECT * FROM enrolled WHERE student_id = ?", session["id"])
    enrolls = [enroll["course_id"] for enroll in enrolls]
    app.logger.info(enrolls)
    courses = db.execute("SELECT * FROM courses WHERE course_id IN (?)", enrolls)
    app.logger.info(courses)
    return render_template("your-courses.html", courses=courses)


@app.route("/course/<id>", methods=["GET", "POST"])
def course(id):
    if request.method == "POST":
        id = request.form.get("id")
        course = db.execute("SELECT * FROM courses WHERE course_id = ?", id)
        enrolled = db.execute("SELECT * FROM enrolled WHERE course_id = ? AND student_id = ?", id, session["id"])
        if len(course) == 0:
            return render_template("error.html", code=404, description="Course not found")
        if len(enrolled) != 0:
            return render_template("error.html", code=405, description="Course already enrolled")
        db.execute("INSERT INTO enrolled (course_id, student_id) VALUES (?, ?)", id, session["id"])
        return redirect("/")
    else:
        course = db.execute("SELECT * FROM courses WHERE course_id = ?", id)
        if len(course) == 0:
            return render_template("error.html", code=404, description="Course not found")
        else:
            course = course[0]
            return render_template("course.html", course=course)
