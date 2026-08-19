from functools import wraps

from flask import abort, redirect, url_for, session

from models.user import User
from models.role_permission import RolePermission
from models.permission import Permission


def current_user():
    """
    Return the currently logged-in User object.

    Uses the existing session-based authentication system.
    """
    user_id = session.get("user_id")

    if not user_id:
        return None

    return User.query.get(user_id)


def has_permission(permission_name):
    """
    Check whether the currently logged-in user has a
    specific permission.

    Example:
        has_permission("sales.view")
        has_permission("sales.create")
    """

    user = current_user()

    if not user or not user.is_active:
        return False

    # ------------------------------------------------------
    # SUPER ADMINISTRATOR
    # ------------------------------------------------------
    #
    # Super Administrator always has full access.
    #
    if user.role and user.role.name == "Super Administrator":
        return True

    # ------------------------------------------------------
    # USER MUST HAVE AN ACTIVE ROLE
    # ------------------------------------------------------

    if not user.role or not user.role.is_active:
        return False

    # ------------------------------------------------------
    # FIND PERMISSION
    # ------------------------------------------------------

    permission = Permission.query.filter_by(
        name=permission_name,
        is_active=True,
    ).first()

    if not permission:
        return False

    # ------------------------------------------------------
    # CHECK ROLE ASSIGNMENT
    # ------------------------------------------------------

    assignment = RolePermission.query.filter_by(
        role_id=user.role_id,
        permission_id=permission.id,
    ).first()

    return assignment is not None


def permission_required(permission_name):
    """
    Decorator for protecting Flask routes.

    Example:

        @sale_bp.route("/create")
        @permission_required("sales.create")
        def create():
            ...
    """

    def decorator(view_function):

        @wraps(view_function)
        def wrapped(*args, **kwargs):

            # --------------------------------------------------
            # NOT LOGGED IN
            # --------------------------------------------------

            if not session.get("user_id"):
                return redirect(url_for("auth.login"))

            # --------------------------------------------------
            # PERMISSION CHECK
            # --------------------------------------------------

            if not has_permission(permission_name):
                abort(403)

            return view_function(*args, **kwargs)

        return wrapped

    return decorator
