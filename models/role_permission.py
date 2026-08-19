from db import db


class RolePermission(db.Model):
    """
    Connects roles to permissions.

    A role can have many permissions.
    A permission can belong to many roles.
    """

    __tablename__ = "role_permissions"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    role = db.relationship(
        "Role",
        backref=db.backref(
            "role_permissions",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )

    permission = db.relationship(
        "Permission",
        backref=db.backref(
            "role_permissions",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission",
        ),
    )

    def __repr__(self):
        return (
            f"<RolePermission "
            f"role={self.role_id} "
            f"permission={self.permission_id}>"
        )
