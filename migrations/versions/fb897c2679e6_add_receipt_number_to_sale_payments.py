"""add receipt number to sale payments

Revision ID: fb897c2679e6
Revises: 42cdbf6be0ec
Create Date: 2026-08-18
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "fb897c2679e6"
down_revision = "42cdbf6be0ec"
branch_labels = None
depends_on = None


def upgrade():

    # ==========================================================
    # 1. ADD RECEIPT NUMBER TEMPORARILY AS NULLABLE
    # ==========================================================
    #
    # Existing sale_payments records already exist.
    #
    # We therefore cannot add the column as NOT NULL
    # immediately.
    #
    # First create it as nullable, populate every existing
    # payment, then enforce NOT NULL below.
    #
    op.add_column(
        "sale_payments",
        sa.Column(
            "receipt_number",
            sa.String(length=50),
            nullable=True,
        ),
    )

    # ==========================================================
    # 2. GENERATE RECEIPT NUMBERS FOR EXISTING PAYMENTS
    # ==========================================================
    #
    # Existing payments are ordered by their payment ID.
    #
    # The first existing payment becomes:
    #
    # RCT-2026-000001
    #
    # The next:
    #
    # RCT-2026-000002
    #
    # etc.
    #
    # We deliberately use the payment ID to guarantee that
    # every existing payment receives a deterministic,
    # unique receipt number.
    #
    connection = op.get_bind()

    payments = connection.execute(sa.text("""
            SELECT id
            FROM sale_payments
            ORDER BY id ASC
            """)).fetchall()

    for sequence, payment in enumerate(payments, start=1):

        receipt_number = f"RCT-2026-{sequence:06d}"

        connection.execute(
            sa.text("""
                UPDATE sale_payments
                SET receipt_number = :receipt_number
                WHERE id = :payment_id
                """),
            {
                "receipt_number": receipt_number,
                "payment_id": payment.id,
            },
        )

    # ==========================================================
    # 3. VERIFY THAT EVERY PAYMENT RECEIVED A NUMBER
    # ==========================================================

    missing_count = connection.execute(sa.text("""
            SELECT COUNT(*)
            FROM sale_payments
            WHERE receipt_number IS NULL
            """)).scalar()

    if missing_count:
        raise RuntimeError(
            "Receipt migration failed: "
            f"{missing_count} payment(s) have no receipt number."
        )

    # ==========================================================
    # 4. VERIFY RECEIPT NUMBERS ARE UNIQUE
    # ==========================================================

    duplicate_count = connection.execute(sa.text("""
            SELECT COUNT(*)
            FROM (
                SELECT receipt_number
                FROM sale_payments
                GROUP BY receipt_number
                HAVING COUNT(*) > 1
            ) AS duplicates
            """)).scalar()

    if duplicate_count:
        raise RuntimeError(
            "Receipt migration failed: duplicate receipt numbers " "were detected."
        )

    # ==========================================================
    # 5. MAKE RECEIPT NUMBER REQUIRED
    # ==========================================================

    with op.batch_alter_table(
        "sale_payments",
        schema=None,
    ) as batch_op:

        batch_op.alter_column(
            "receipt_number",
            existing_type=sa.String(length=50),
            nullable=False,
        )

    # ==========================================================
    # 6. ADD UNIQUE INDEX
    # ==========================================================

    op.create_index(
        "ix_sale_payments_receipt_number",
        "sale_payments",
        ["receipt_number"],
        unique=True,
    )


def downgrade():

    # Remove the unique index first.
    op.drop_index(
        "ix_sale_payments_receipt_number",
        table_name="sale_payments",
    )

    # Then remove the receipt number column.
    op.drop_column(
        "sale_payments",
        "receipt_number",
    )
