from db import db

from models.permission import Permission
from models.role import Role
from models.role_permission import RolePermission


class PermissionService:

    # ==========================================================
    # PERMISSION CATALOG
    # ==========================================================

    PERMISSIONS = [
        # Dashboard
        ("dashboard", "view", "View dashboard"),
        # Products
        ("products", "view", "View products"),
        ("products", "create", "Create products"),
        ("products", "edit", "Edit products"),
        ("products", "delete", "Delete products"),
        # Categories
        ("categories", "view", "View categories"),
        ("categories", "create", "Create categories"),
        ("categories", "edit", "Edit categories"),
        ("categories", "delete", "Delete categories"),
        # Brands
        ("brands", "view", "View brands"),
        ("brands", "create", "Create brands"),
        ("brands", "edit", "Edit brands"),
        ("brands", "delete", "Delete brands"),
        # Inventory
        ("inventory", "view", "View inventory"),
        ("inventory", "create", "Create inventory records"),
        ("inventory", "edit", "Edit inventory records"),
        ("inventory", "delete", "Delete inventory records"),
        ("inventory", "adjust", "Adjust inventory quantities"),
        ("inventory", "change_price", "Change inventory prices"),
        # IMEI
        ("imei", "view", "View IMEI records"),
        ("imei", "create", "Create IMEI records"),
        ("imei", "edit", "Edit IMEI records"),
        ("imei", "delete", "Delete IMEI records"),
        ("imei", "assign", "Assign IMEI"),
        ("imei", "release", "Release IMEI"),
        # Purchases
        ("purchases", "view", "View purchases"),
        ("purchases", "create", "Create purchases"),
        ("purchases", "edit", "Edit purchases"),
        ("purchases", "delete", "Delete purchases"),
        ("purchases", "receive", "Receive purchases"),
        ("purchases", "cancel", "Cancel purchases"),
        # Suppliers
        ("suppliers", "view", "View suppliers"),
        ("suppliers", "create", "Create suppliers"),
        ("suppliers", "edit", "Edit suppliers"),
        ("suppliers", "delete", "Delete suppliers"),
        # Customers
        ("customers", "view", "View customers"),
        ("customers", "create", "Create customers"),
        ("customers", "edit", "Edit customers"),
        ("customers", "delete", "Delete customers"),
        # Sales
        ("sales", "view", "View sales"),
        ("sales", "create", "Create sales"),
        ("sales", "edit", "Edit sales"),
        ("sales", "cancel", "Cancel sales"),
        ("sales", "refund", "Refund sales"),
        ("sales", "override_price", "Override selling price"),
        # Payments
        ("payments", "view", "View payments"),
        ("payments", "create", "Create payments"),
        ("payments", "edit", "Edit payments"),
        ("payments", "delete", "Delete payments"),
        # Customer Credit
        ("credit", "view", "View customer credit"),
        ("credit", "create", "Create customer credit"),
        ("credit", "adjust", "Adjust customer credit"),
        ("credit", "settle", "Settle customer credit"),
        # Trade-ins
        ("tradeins", "view", "View trade-ins"),
        ("tradeins", "create", "Create trade-ins"),
        ("tradeins", "edit", "Edit trade-ins"),
        ("tradeins", "delete", "Delete trade-ins"),
        ("tradeins", "approve", "Approve trade-ins"),
        # Expenses
        ("expenses", "view", "View expenses"),
        ("expenses", "create", "Create expenses"),
        ("expenses", "edit", "Edit expenses"),
        ("expenses", "delete", "Delete expenses"),
        # Reports
        ("reports", "view", "View reports"),
        ("reports", "export", "Export reports"),
        # Users
        ("users", "view", "View users"),
        ("users", "create", "Create users"),
        ("users", "edit", "Edit users"),
        ("users", "disable", "Enable/disable users"),
        ("users", "reset_password", "Reset user passwords"),
        # Roles
        ("roles", "view", "View roles"),
        ("roles", "create", "Create roles"),
        ("roles", "edit", "Edit roles"),
        ("roles", "delete", "Delete roles"),
        # Permissions
        ("permissions", "view", "View permissions"),
        ("permissions", "assign", "Assign permissions to roles"),
        # System Settings
        ("settings", "view", "View system settings"),
        ("settings", "edit", "Edit system settings"),
        # Backup
        ("backup", "view", "View backups"),
        ("backup", "create", "Create backups"),
        ("backup", "restore", "Restore backups"),
        ("backup", "delete", "Delete backups"),
        # Notifications
        ("notifications", "view", "View notifications"),
        ("notifications", "manage", "Manage notifications"),
    ]

    # ==========================================================
    # DEFAULT ROLE PERMISSIONS
    # ==========================================================

    DEFAULT_ROLE_PERMISSIONS = {
        "Super Administrator": {
            "*",
        },
        "Administrator": {
            "dashboard.view",
            "products.*",
            "categories.*",
            "brands.*",
            "inventory.*",
            "imei.*",
            "purchases.*",
            "suppliers.*",
            "customers.*",
            "sales.*",
            "payments.*",
            "credit.*",
            "tradeins.*",
            "expenses.*",
            "reports.*",
            "users.view",
            "users.create",
            "users.edit",
            "users.disable",
            "users.reset_password",
            "notifications.*",
        },
        "Inventory Manager": {
            "dashboard.view",
            "products.*",
            "categories.*",
            "brands.*",
            "inventory.*",
            "imei.*",
            "purchases.*",
            "suppliers.*",
            "customers.view",
            "reports.view",
            "reports.export",
            "tradeins.view",
            "tradeins.create",
            "tradeins.edit",
            "notifications.view",
        },
        "Sales Manager": {
            "dashboard.view",
            "products.view",
            "categories.view",
            "brands.view",
            "inventory.view",
            "imei.view",
            "customers.*",
            "sales.*",
            "payments.*",
            "credit.*",
            "tradeins.*",
            "reports.view",
            "reports.export",
            "notifications.view",
        },
        "Sales Person": {
            "dashboard.view",
            "products.view",
            "categories.view",
            "brands.view",
            "inventory.view",
            "imei.view",
            "customers.view",
            "customers.create",
            "customers.edit",
            "sales.view",
            "sales.create",
            "payments.view",
            "payments.create",
            "credit.view",
            "tradeins.view",
            "tradeins.create",
            "reports.view",
            "notifications.view",
        },
        "Technician": {
            "dashboard.view",
            "products.view",
            "inventory.view",
            "imei.*",
            "customers.view",
            "tradeins.view",
            "tradeins.create",
            "tradeins.edit",
            "reports.view",
            "notifications.view",
        },
        "Accountant": {
            "dashboard.view",
            "customers.view",
            "sales.view",
            "payments.*",
            "credit.*",
            "purchases.view",
            "suppliers.view",
            "expenses.*",
            "tradeins.view",
            "reports.*",
            "notifications.view",
        },
    }

    # ==========================================================
    # CREATE PERMISSION
    # ==========================================================

    @staticmethod
    def get_or_create_permission(module, action, description=None):

        name = f"{module}.{action}"

        permission = Permission.query.filter_by(name=name).first()

        if permission:
            return permission

        permission = Permission(
            name=name,
            module=module,
            action=action,
            description=description,
            is_active=True,
        )

        db.session.add(permission)

        return permission

    # ==========================================================
    # SEED PERMISSIONS
    # ==========================================================

    @classmethod
    def seed_permissions(cls):

        created = 0

        for module, action, description in cls.PERMISSIONS:

            permission = Permission.query.filter_by(name=f"{module}.{action}").first()

            if permission:
                continue

            cls.get_or_create_permission(
                module=module,
                action=action,
                description=description,
            )

            created += 1

        db.session.commit()

        return created

    # ==========================================================
    # MATCH PERMISSION
    # ==========================================================

    @staticmethod
    def permission_matches(permission_name, requested):

        if requested == permission_name:
            return True

        if permission_name.endswith(".*"):

            prefix = permission_name[:-2]

            return requested.startswith(prefix + ".")

        return False

    # ==========================================================
    # ASSIGN PERMISSION
    # ==========================================================

    @staticmethod
    def assign_permission(role, permission):

        existing = RolePermission.query.filter_by(
            role_id=role.id,
            permission_id=permission.id,
        ).first()

        if existing:
            return existing

        assignment = RolePermission(
            role_id=role.id,
            permission_id=permission.id,
        )

        db.session.add(assignment)

        return assignment

    # ==========================================================
    # SEED ROLE PERMISSIONS
    # ==========================================================

    @classmethod
    def seed_role_permissions(cls):

        assigned = 0

        for role_name, requested_permissions in cls.DEFAULT_ROLE_PERMISSIONS.items():

            role = Role.query.filter_by(name=role_name).first()

            if not role:
                continue

            if "*" in requested_permissions:

                permissions = Permission.query.filter_by(is_active=True).all()

            else:

                permissions = Permission.query.filter_by(is_active=True).all()

                permissions = [
                    permission
                    for permission in permissions
                    if any(
                        cls.permission_matches(
                            requested,
                            permission.name,
                        )
                        for requested in requested_permissions
                    )
                ]

            for permission in permissions:

                existing = RolePermission.query.filter_by(
                    role_id=role.id,
                    permission_id=permission.id,
                ).first()

                if existing:
                    continue

                cls.assign_permission(
                    role,
                    permission,
                )

                assigned += 1

        db.session.commit()

        return assigned
