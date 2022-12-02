from functools import wraps
from consts import yt_link_pattern
import secrets
import os

def required_login(f):
    from flask import session, redirect
    @wraps(f)
    def wrapper():
        if not session.get("username"):
            return redirect("/login")
        else:
            return f()
    return wrapper


def video_id(link):
    match = yt_link_pattern.search(link)
    if match == None:
        return None
    else:
        return match[4]


def youtube_link(link):
    return "https://www.youtube.com/embed/" + link
# def save_file(file):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(file.filename)
#     f_name = random_hex + f_ext
#     f_path = os.path.join(app.root_path, 'static/files', f_name)
#     file.save(f_path)
#     return f_name

