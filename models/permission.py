from db import db


class Permission(db.Model):
    """
    Defines an individual system permission.

    Examples:
    - sales.view
    - sales.create
    - sales.cancel
    - inventory.adjust
    - users.manage
    """

    __tablename__ = "permissions"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    module = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    action = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(255),
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self):
        return f"<Permission {self.name}>"
