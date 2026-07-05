from flask import render_template, request, redirect, session, flash
from app import app
from db import cursor


# ==========================================
# Login
# ==========================================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
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

        flash("Invalid username or password.")

    return render_template("login.html")


# ==========================================
# Logout
# ==========================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")