from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from services.user_service import UserService
from models.system_setting import SystemSetting

from utils.auth import login_required
from utils.permissions import permission_required

user_bp = Blueprint("user", __name__, url_prefix="/users")


# ==========================================
# VIEW USERS
# ==========================================

@user_bp.route("/")
@permission_required("users.view")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

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

    if not login_required():
        return redirect(url_for("auth.login"))

    roles = UserService.get_all_roles()

    if request.method == "POST":

        success, message = UserService.create_user(request.form)

        flash(message, "success" if success else "danger")

        if success:
            return redirect(url_for("user.index"))

    return render_template(
        "users/create.html",
        roles=roles,
    )


# ==========================================
# EDIT USER
# ==========================================

@user_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@permission_required("users.edit")
def edit(user_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    roles = UserService.get_all_roles()

    if request.method == "POST":

        success, message = UserService.update_user(
            user,
            request.form,
        )

        flash(
            message,
            "success" if success else "danger",
        )

        if success:
            return redirect(url_for("user.index"))

    return render_template(
        "users/edit.html",
        user=user,
        roles=roles,
    )


# ==========================================
# CHANGE PASSWORD
# ==========================================

@user_bp.route("/password/<int:user_id>", methods=["POST"])
@permission_required("users.reset_password")
def change_password(user_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    password = request.form.get("password")

    if not password:
        flash("Password cannot be empty.", "danger")
        return redirect(
            url_for(
                "user.edit",
                user_id=user.id,
            )
        )

    UserService.change_password(
        user,
        password,
    )

    flash(
        "Password changed successfully.",
        "success",
    )

    return redirect(
        url_for(
            "user.edit",
            user_id=user.id,
        )
    )


# ==========================================
# ACTIVATE / DEACTIVATE USER
# ==========================================

@user_bp.route("/toggle/<int:user_id>")
@permission_required("users.disable")
def toggle(user_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    UserService.toggle_status(user)

    flash(
        "User status updated.",
        "success",
    )

    return redirect(url_for("user.index"))


# ==========================================
# PROFILE
# ==========================================

@user_bp.route("/profile/<int:user_id>")
@permission_required("users.view")
def profile(user_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    user = UserService.get_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("user.index"))

    return render_template(
        "users/profile.html",
        user=user,
    )
