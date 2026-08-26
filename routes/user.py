from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from services.user_service import UserService
from models.system_setting import SystemSetting
from models.user import User

from utils.auth import login_required
from utils.permissions import permission_required

user_bp = Blueprint("user", __name__, url_prefix="/users")


# ==========================================
# VIEW USERS
# ==========================================

@user_bp.route("/")
@permission_required("users.view")
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    role = request.args.get("role", "").strip()
    status = request.args.get("status", "").strip()
    settings = SystemSetting.get_settings()

    users = UserService.get_users(
        page=page,
        per_page=settings.records_per_page,
        search=search,
        role=role,
        status=status,
    )

    stats = UserService.get_statistics()
    roles = UserService.get_all_roles()

    return render_template(
        "users/index.html",
        users=users,
        stats=stats,
        roles=roles,
        search=search,
        selected_role=role,
        selected_status=status,
    )


# ==========================================
# CREATE USER
# ==========================================

@user_bp.route("/create", methods=["GET", "POST"])
@permission_required("users.create")
def create():
    roles = UserService.get_all_roles()

    if request.method == "POST":
        success, message = UserService.create_user(request.form)
        flash(message, "success" if success else "danger")

        if success:
            return redirect(url_for("user.index"))

    return render_template("users/create.html", roles=roles)


# ==========================================
# EDIT USER (ADMIN / AUTHORIZED STAFF)
# ==========================================

@user_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@permission_required("users.edit")
def edit(user_id):
    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    roles = UserService.get_all_roles()

    if request.method == "POST":
        success, message = UserService.update_user(user, request.form)

        flash(message, "success" if success else "danger")

        if success:
            return redirect(url_for("user.index"))

    return render_template("users/edit.html", user=user, roles=roles)


# ==========================================
# MY PROFILE — AVAILABLE TO EVERY LOGGED-IN USER
# ==========================================

@user_bp.route("/me", methods=["GET", "POST"])
def me():
    if not login_required():
        return redirect(url_for("auth.login"))

    user = User.query.get(session.get("user_id"))

    if not user or not user.is_active:
        session.clear()
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        success, message = UserService.update_own_profile(user, request.form)
        flash(message, "success" if success else "danger")

        if success:
            session["username"] = user.username
            return redirect(url_for("user.me"))

    return render_template("users/me.html", user=user)


# ==========================================
# CHANGE OWN PASSWORD
# ==========================================

@user_bp.route("/me/password", methods=["POST"])
def change_own_password():
    if not login_required():
        return redirect(url_for("auth.login"))

    user = User.query.get(session.get("user_id"))

    if not user or not user.is_active:
        session.clear()
        return redirect(url_for("auth.login"))

    current_password = request.form.get("current_password", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not user.check_password(current_password):
        flash("Your current password is incorrect.", "danger")
        return redirect(url_for("user.me"))

    if password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("user.me"))

    success, message = UserService.change_own_password(user, password)
    flash(message, "success" if success else "danger")
    return redirect(url_for("user.me"))


# ==========================================
# ADMIN RESET PASSWORD
# ==========================================

@user_bp.route("/password/<int:user_id>", methods=["POST"])
@permission_required("users.reset_password")
def change_password(user_id):
    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    password = request.form.get("password")

    if not password:
        flash("Password cannot be empty.", "danger")
        return redirect(url_for("user.edit", user_id=user.id))

    UserService.change_password(user, password)

    flash("Password changed successfully.", "success")

    return redirect(url_for("user.edit", user_id=user.id))


# ==========================================
# ACTIVATE / DEACTIVATE USER
# ==========================================

@user_bp.route("/toggle/<int:user_id>", methods=["POST"])
@permission_required("users.disable")
def toggle(user_id):
    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    # Never allow an administrator to accidentally disable the account
    # that is currently being used for this request.
    if user.id == session.get("user_id") and user.is_active:
        flash("You cannot deactivate your own active account.", "warning")
        return redirect(url_for("user.index"))

    UserService.toggle_status(user)

    flash("User status updated.", "success")
    return redirect(url_for("user.index"))


# ==========================================
# PROFILE VIEW — ADMIN / AUTHORIZED STAFF
# ==========================================

@user_bp.route("/profile/<int:user_id>")
@permission_required("users.view")
def profile(user_id):
    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    return render_template("users/profile.html", user=user)
