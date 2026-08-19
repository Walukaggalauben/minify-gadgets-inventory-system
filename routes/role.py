from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from services.role_service import RoleService
from utils.auth import login_required
from utils.permissions import permission_required

role_bp = Blueprint(
    "role",
    __name__,
    url_prefix="/users/roles",
)


# ==========================================================
# ROLES LIST
# ==========================================================


@role_bp.route("/")
@permission_required("roles.view")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

    roles = RoleService.get_all_roles()

    role_data = []

    for role in roles:

        role_data.append(
            {
                "role": role,
                "permission_count": RoleService.get_permission_count(role.id),
            }
        )

    return render_template(
        "roles/index.html",
        roles=role_data,
    )


# ==========================================================
# MANAGE ROLE PERMISSIONS
# ==========================================================


@role_bp.route(
    "/<int:role_id>",
    methods=["GET", "POST"],
)
@permission_required("roles.edit")
def permissions(role_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    role = RoleService.get_role(role_id)

    if request.method == "POST":

        permission_ids = request.form.getlist("permission_ids")

        success, message = RoleService.update_permissions(
            role.id,
            permission_ids,
        )

        flash(
            message,
            "success" if success else "danger",
        )

        if success:
            return redirect(
                url_for(
                    "role.permissions",
                    role_id=role.id,
                )
            )

    grouped_permissions = RoleService.get_permissions_by_module()

    selected_permission_ids = RoleService.get_role_permission_ids(role.id)

    return render_template(
        "roles/permissions.html",
        role=role,
        grouped_permissions=grouped_permissions,
        selected_permission_ids=selected_permission_ids,
    )
