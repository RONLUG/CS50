from functools import wraps
from consts import yt_link_pattern

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