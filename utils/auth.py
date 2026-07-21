from flask import session


def login_required():
    return "user_id" in session