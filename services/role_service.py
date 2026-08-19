from db import db
from models.role import Role
from models.permission import Permission
from models.role_permission import RolePermission


class RoleService:

    # ==========================================================
    # GET ROLES
    # ==========================================================

    @staticmethod
    def get_all_roles():
        return Role.query.order_by(Role.name.asc()).all()

    # ==========================================================
    # GET ROLE
    # ==========================================================

    @staticmethod
    def get_role(role_id):
        return Role.query.get_or_404(role_id)

    # ==========================================================
    # GET ALL ACTIVE PERMISSIONS
    # ==========================================================

    @staticmethod
    def get_all_permissions():
        return (
            Permission.query.filter_by(is_active=True)
            .order_by(Permission.module.asc(), Permission.action.asc())
            .all()
        )

    # ==========================================================
    # GROUP PERMISSIONS BY MODULE
    # ==========================================================

    @staticmethod
    def get_permissions_by_module():
        permissions = RoleService.get_all_permissions()

        grouped = {}

        for permission in permissions:
            grouped.setdefault(permission.module, []).append(permission)

        return grouped

    # ==========================================================
    # GET ROLE PERMISSIONS
    # ==========================================================

    @staticmethod
    def get_role_permission_ids(role_id):

        assignments = RolePermission.query.filter_by(role_id=role_id).all()

        return {assignment.permission_id for assignment in assignments}

    # ==========================================================
    # GET ROLE PERMISSION COUNT
    # ==========================================================

    @staticmethod
    def get_permission_count(role_id):

        return RolePermission.query.filter_by(role_id=role_id).count()

    # ==========================================================
    # UPDATE ROLE PERMISSIONS
    # ==========================================================

    @staticmethod
    def update_permissions(role_id, permission_ids):

        role = RoleService.get_role(role_id)

        # ------------------------------------------------------
        # SAFETY: SUPER ADMINISTRATOR ALWAYS HAS EVERYTHING
        # ------------------------------------------------------

        if role.name == "Super Administrator":

            return False, ("Super Administrator permissions cannot be " "restricted.")

        try:

            permission_ids = {int(permission_id) for permission_id in permission_ids}

        except (TypeError, ValueError):

            return False, "Invalid permission selection."

        valid_ids = {
            permission.id
            for permission in Permission.query.filter(
                Permission.is_active.is_(True), Permission.id.in_(permission_ids)
            ).all()
        }

        # ------------------------------------------------------
        # REMOVE EXISTING ASSIGNMENTS
        # ------------------------------------------------------

        RolePermission.query.filter_by(role_id=role.id).delete(
            synchronize_session=False
        )

        # ------------------------------------------------------
        # ADD NEW ASSIGNMENTS
        # ------------------------------------------------------

        for permission_id in valid_ids:

            db.session.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission_id,
                )
            )

        db.session.commit()

        return True, (f"Permissions updated successfully for " f"{role.name}.")
