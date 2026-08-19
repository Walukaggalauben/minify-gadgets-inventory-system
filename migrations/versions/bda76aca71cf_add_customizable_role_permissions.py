"""add customizable role permissions

Revision ID: bda76aca71cf
Revises: fb897c2679e6
Create Date: 2026-08-19 10:10:39.588784

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "bda76aca71cf"
down_revision = "fb897c2679e6"
branch_labels = None
depends_on = None


def upgrade():

    # ==========================================================
    # PERMISSIONS
    # ==========================================================

    op.create_table(
        "permissions",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "module",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.UniqueConstraint(
            "name",
            name="uq_permissions_name",
        ),
    )

    op.create_index(
        "ix_permissions_name",
        "permissions",
        ["name"],
        unique=True,
    )

    op.create_index(
        "ix_permissions_module",
        "permissions",
        ["module"],
        unique=False,
    )

    op.create_index(
        "ix_permissions_action",
        "permissions",
        ["action"],
        unique=False,
    )

    # ==========================================================
    # ROLE PERMISSIONS
    # ==========================================================

    op.create_table(
        "role_permissions",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_role_permissions_role",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_permissions_permission",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission",
        ),
    )

    op.create_index(
        "ix_role_permissions_role_id",
        "role_permissions",
        ["role_id"],
        unique=False,
    )

    op.create_index(
        "ix_role_permissions_permission_id",
        "role_permissions",
        ["permission_id"],
        unique=False,
    )


def downgrade():

    op.drop_index(
        "ix_role_permissions_permission_id",
        table_name="role_permissions",
    )

    op.drop_index(
        "ix_role_permissions_role_id",
        table_name="role_permissions",
    )

    op.drop_table("role_permissions")

    op.drop_index(
        "ix_permissions_action",
        table_name="permissions",
    )

    op.drop_index(
        "ix_permissions_module",
        table_name="permissions",
    )

    op.drop_index(
        "ix_permissions_name",
        table_name="permissions",
    )

    op.drop_table("permissions")
