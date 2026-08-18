"""add customer overpayment settlement ledger

Revision ID: a7e9b1c42d17
Revises: 98f8f02a656b
Create Date: 2026-08-15

"""
from alembic import op
import sqlalchemy as sa


revision = "a7e9b1c42d17"
down_revision = "98f8f02a656b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "customer_credits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("original_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("remaining_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sale_id"),
    )

    op.create_table(
        "customer_credit_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("credit_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=30), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=True),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("processed_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["credit_id"], ["customer_credits.id"]),
        sa.ForeignKeyConstraint(["processed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Backfill existing sale overpayments so old transactions such as
    # Sale #22 immediately become visible as customer credit.
    op.execute(sa.text("""
        INSERT INTO customer_credits
            (customer_id, sale_id, original_amount, remaining_amount,
             status, created_at, updated_at)
        SELECT
            s.customer_id,
            s.id,
            ROUND(COALESCE(s.amount_paid, 0) - COALESCE(s.total_amount, 0), 2),
            ROUND(COALESCE(s.amount_paid, 0) - COALESCE(s.total_amount, 0), 2),
            'Outstanding',
            NOW(),
            NOW()
        FROM sales s
        WHERE COALESCE(s.amount_paid, 0) > COALESCE(s.total_amount, 0)
          AND NOT EXISTS (
              SELECT 1
              FROM customer_credits cc
              WHERE cc.sale_id = s.id
          )
    """))


def downgrade():
    op.drop_table("customer_credit_transactions")
    op.drop_table("customer_credits")
