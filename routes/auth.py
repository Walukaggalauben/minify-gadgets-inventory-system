<<<<<<< HEAD
from flask import render_template, request, redirect, session, flash
from app import app
from db import cursor


# ==========================================
# Login
# ==========================================
@app.route("/", methods=["GET", "POST"])
=======
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)

from services.auth_service import AuthService

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/", methods=["GET", "POST"])
>>>>>>> main
def login():

    if request.method == "POST":

        username = request.form["username"]
<<<<<<< HEAD
        password = request.form["password"]

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username=%s
            AND password=%s
            LIMIT 1
        """, (username, password))

        user = cursor.fetchone()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/dashboard")
=======

        password = request.form["password"]

        user = AuthService.authenticate(
            username,
            password
        )

        if user:

            session["user_id"] = user.id

            session["username"] = user.username

            session["role"] = user.role.name

            return redirect(url_for("dashboard.dashboard"))
>>>>>>> main

        flash("Invalid username or password.")

    return render_template("login.html")


<<<<<<< HEAD
# ==========================================
# Logout
# ==========================================
@app.route("/logout")
=======
@auth_bp.route("/logout")
>>>>>>> main
def logout():

    session.clear()

    return redirect("/")