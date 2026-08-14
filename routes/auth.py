from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
)

from services.auth_service import AuthService



auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = AuthService.authenticate(username, password)

        if user:

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role.name if user.role else ""
            session["last_activity"] = datetime.utcnow().timestamp()
            user.last_login = datetime.utcnow()
            from db import db

            db.session.commit()

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))
