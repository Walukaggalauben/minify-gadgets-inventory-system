from utils.timezone import utc_now_naive

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
from services.password_reset_service import PasswordResetService


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        identifier = (
            request.form.get("identifier")
            or request.form.get("username")
            or ""
        ).strip()

        password = request.form.get("password", "")

        user = AuthService.authenticate(identifier, password)

        if user:

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role.name if user.role else ""
            session["last_activity"] = utc_now_naive().timestamp()

            user.last_login = utc_now_naive()

            from db import db
            db.session.commit()

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username, phone, email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        PasswordResetService.request_reset(
            email,
            lambda token: url_for("auth.reset_password", token=token, _external=True),
        )

        # Deliberately generic: do not reveal whether an email belongs to an account.
        flash(
            "If an active account uses that email address, a password reset link has been sent.",
            "info",
        )
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = PasswordResetService.load_token(token)

    if not user:
        flash("This password reset link is invalid or has expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/reset_password.html")

        success, message = PasswordResetService.reset_password(user, password)
        flash(message, "success" if success else "danger")

        if success:
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
