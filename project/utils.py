from functools import wraps
from consts import yt_link_pattern
import secrets
import os
from flask import redirect, session

def required_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("username"):
            return redirect("/login")
        else:
            return f(*args, **kwargs)
    return wrapper


def video_id(link):
    match = yt_link_pattern.search(link)
    if match == None:
        return None
    else:
        return match[4]


def youtube_link(link):
    return "https://www.youtube.com/embed/" + link

