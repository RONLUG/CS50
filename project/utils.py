from functools import wraps
import re

def required_login(f):
    from flask import session, redirect
    @wraps(f)
    def wrapper():
        if not session.get("username"):
            return redirect("/login")
        else:
            return f()
    return wrapper


def is_youtube_link(link):
    pass