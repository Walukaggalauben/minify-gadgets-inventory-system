"""add expenses and sale payments

Revision ID: 5381ad063fda
Revises: deb125b58f78
Create Date: 2026-08-12 18:30:50.432309

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5381ad063fda"
down_revision = "deb125b58f78"
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # EXPENSES
    # ============================================================

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expense_number", sa.String(length=40), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column(
            "payment_method",
            sa.String(length=30),
            nullable=False,
            server_default="Cash",
        ),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("expense_number"),
    )

    # ============================================================
    # SALE PAYMENTS
    # ============================================================

    op.create_table(
        "sale_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=False),
        sa.Column("payment_date", sa.DateTime(), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("received_by", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["received_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # SALES — ADD PAYMENT / INSTALLMENT FIELDS SAFELY
    #
    # Existing sales already exist in the database.
    # Therefore these fields are temporarily nullable.
    # We populate historical records before making them required.
    # ============================================================

    with op.batch_alter_table("sales", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "amount_paid",
                sa.Numeric(precision=15, scale=2),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "balance_due",
                sa.Numeric(precision=15, scale=2),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "payment_status",
                sa.String(length=20),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "due_date",
                sa.Date(),
                nullable=True,
            )
        )

    # ============================================================
    # INITIALIZE EXISTING SALES
    #
    # Existing sales are legacy completed sales. Since the old
    # schema did not track installment payments separately,
    # initialize them as fully paid.
    # ============================================================

    op.execute(
        """
        UPDATE sales
        SET
            amount_paid = COALESCE(total_amount, 0),
            balance_due = 0,
            payment_status = 'Paid'
        """
    )

    # ============================================================
    # MAKE REQUIRED FIELDS NON-NULL AFTER BACKFILL
    # ============================================================

    with op.batch_alter_table("sales", schema=None) as batch_op:
        batch_op.alter_column(
            "amount_paid",
            existing_type=sa.Numeric(precision=15, scale=2),
            nullable=False,
        )

        batch_op.alter_column(
            "balance_due",
            existing_type=sa.Numeric(precision=15, scale=2),
            nullable=False,
        )

        batch_op.alter_column(
            "payment_status",
            existing_type=sa.String(length=20),
            nullable=False,
        )


def downgrade():
    # ============================================================
    # REMOVE SALES PAYMENT / INSTALLMENT FIELDS
    # ============================================================

    with op.batch_alter_table("sales", schema=None) as batch_op:
        batch_op.drop_column("due_date")
        batch_op.drop_column("payment_status")
        batch_op.drop_column("balance_due")
        batch_op.drop_column("amount_paid")

    # ============================================================
    # REMOVE SALE PAYMENTS
    # ============================================================

    op.drop_table("sale_payments")

    # ============================================================
    # REMOVE EXPENSES
    # ============================================================

    op.drop_table("expenses")