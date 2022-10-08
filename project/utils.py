from functools import wraps

def required_login(f):
    from flask import session, redirect
    @wraps(f)
    def wrapper():
        if not session.get("username"):
            return redirect("/login")
        else:
            return f()
    return wrapper
