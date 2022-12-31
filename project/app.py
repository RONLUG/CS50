from cs50 import SQL
from flask import Flask, render_template, request, session, redirect, send_file
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from utils import required_login, video_id, youtube_link
from consts import tags
import secrets
import os

app = Flask(__name__)
app.secret_key = "cf0d91a5c204a957c085f9fbca02e6ca2e904410acbc473c3d0c13bcc62aabe8"

db = SQL("sqlite:///app.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def save_file(file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    f_name = random_hex + f_ext
    f_path = os.path.join(app.root_path, 'static/files', f_name)
    file.save(f_path)
    return f_name

@app.route("/")
@required_login
def index():
    courses = db.execute("SELECT * FROM courses")
    return render_template("index.html", courses=courses)


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
            session["id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["user_id"]
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


@app.route("/create-course", methods=["GET", "POST"])
@required_login
def create_course():
    if request.method == "POST":
        # Get form data
        title = request.form.get("title")
        desc = request.form.get("description")
        tag = request.form.get("tag")
        intro_vdo = request.form.get("intro_vdo")
        banner = request.files["banner"]
        totalLecture = int(request.form.get("total_lecture"))
        lectures = []
        app.logger.info(totalLecture)
        for i in range(totalLecture):
            lecture = dict()
            lecture["title"] = request.form.get(f"title{i}")
            lecture["video"] = request.form.get(f"video{i}")
            lecture["materials"] = request.files.getlist(f"materials{i}")
            # app.logger.info(f"title: {lecture['title']}")
            # app.logger.info(f"video: {lecture['video']}")
            # app.logger.info(f"materials: {lecture['materials']}")
            lectures.append(lecture)


        # Validate data
        id = db.execute("SELECT user_id FROM users WHERE username=?", session["username"])[0]["user_id"]
        if title == None or desc == None or tag == "tags":
            return render_template("error.html", code=403, description="Required more infomation")
        if tag not in tags:
            return render_template("error.html", code=403, description="Invalid tag")

        # Validate course intro video link
        vdo_link = video_id(intro_vdo)
        if vdo_link == None and intro_vdo != None:
            return render_template("error.html", code="403", description="Invalid intro video url")
        else:
            vdo_link = youtube_link(vdo_link)

        # Add new course to SQL
        db.execute("INSERT INTO courses (title, description, tag, publisher_id, intro_video) VALUES (?, ?, ?, ?, ?)", title, desc, tag, id, vdo_link)
        course_id = db.execute("SELECT * FROM courses WHERE title = ? AND publisher_id = ?", title, id)[0]["course_id"]

        # Save files
        if banner:
            app.logger.info(f"banner{banner}")
            banner_name = save_file(banner)
            db.execute("UPDATE courses SET banner = ? WHERE course_id = ?", banner_name, course_id)

        for lecture in lectures:
            vdo_link = video_id(lecture["video"])
            vdo_link = youtube_link(vdo_link)
            db.execute("INSERT INTO lectures (course_id, title, video) VALUES (?, ?, ?)", course_id, lecture["title"], vdo_link)
            lecture_id = db.execute("SELECT * FROM lectures WHERE course_id = ? AND title = ? AND video = ?", course_id, lecture["title"], vdo_link)[0]["lecture_id"]
            for material in lecture['materials']:
                file_name = save_file(material)
                db.execute("INSERT INTO materials (lecture_id, name) VALUES (?, ?)", lecture_id, file_name)

            app.logger.info(f"len: {len(lectures[i]['materials'])}")
        return redirect("/")
    else:
        return render_template("create-course.html", tags=tags)


@app.route("/<publisher>/<title>", methods=["GET", "POST"])
def course(publisher, title):
    if request.method == "POST":
        id = request.form.get("id")
        course = db.execute("SELECT * FROM courses WHERE course_id = ?", id)
        enrolled = db.execute("SELECT * FROM enrolled WHERE course_id = ? AND student_id = ?", id, session["id"])
        if len(course) == 0:
            return render_template("error.html", code=404, description="Course not found")
        if len(enrolled) != 0:
            # return render_template("error.html", code=405, description="Course already enrolled")
            db.execute("DELETE FROM enrolled WHERE course_id = ? AND student_id = ?", id, session["id"])
        else:
            db.execute("INSERT INTO enrolled (course_id, student_id) VALUES (?, ?)", id, session["id"])
        return redirect(f"/{publisher}/{title}")
    else:
        publisher_id = db.execute("SELECT * FROM users WHERE username = ?", publisher)[0]["user_id"]
        course = db.execute("SELECT * FROM courses WHERE title = ? and publisher_id = ?", title, publisher_id)
        if len(course) == 0:
            return render_template("error.html", code=404, description="Course not found")
        course = course[0]
        enrolled = db.execute("SELECT * FROM enrolled WHERE course_id = ? AND student_id = ?", course["course_id"], session["id"])
        lectures = db.execute("SELECT * FROM lectures WHERE course_id = ?", course["course_id"])
        return render_template("course.html", course=course, publisher=publisher, enrolled=enrolled, lectures=lectures)


@app.route("/course/<id>")
def course_redirect(id):
    course = db.execute("SELECT * FROM courses WHERE course_id = ?", id)
    if course == None:
        return render_template("error.html", code=403, description="course not found")
    else:
        publisher = db.execute("SELECT * FROM users WHERE user_id = ?", course[0]["publisher_id"])[0]["username"]
        return redirect(f"/{publisher}/{course[0]['title']}")

@app.route("/<username>")
@required_login
def profile(username):
    enrolls = db.execute("SELECT * FROM enrolled WHERE student_id = ?", session["id"])
    enrolls = [enroll["course_id"] for enroll in enrolls]
    courses = db.execute("SELECT * FROM courses WHERE course_id IN (?)", enrolls)
    return render_template("profile.html", courses=courses)


@app.route("/<publisher>/<courseTitle>/<lectureTitle>")
def lecture(publisher, courseTitle, lectureTitle):
    publisher_id = db.execute("SELECT * FROM users WHERE username = ?", publisher)[0]["user_id"]
    course_id = db.execute("SELECT * FROM courses WHERE publisher_id = ? AND title = ?", publisher_id, courseTitle)[0]["course_id"]
    lecture = db.execute("SELECT * FROM lectures WHERE course_id = ? AND title = ?", course_id, lectureTitle)[0]
    materials = db.execute("SELECT * FROM materials WHERE lecture_id = ?", lecture["lecture_id"])
    app.logger.info(materials)
    return render_template("lecture.html", publisher=publisher, courseTitle=courseTitle, lecture=lecture, materials=materials)


@app.route("/download/<filename>")
def download(filename):
    p = f"static/files/{filename}"
    return send_file(p, as_attachment=True)
