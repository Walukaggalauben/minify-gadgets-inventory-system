"""feat: add foreign currency payment tracking

Revision ID: d222813d62ce
Revises: afa54a5c7613
Create Date: 2026-08-15 12:23:23.650175

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d222813d62ce"
down_revision = "afa54a5c7613"
branch_labels = None
depends_on = None


def upgrade():

    # ==========================================================
    # 1. ADD NEW COLUMNS TEMPORARILY AS NULLABLE
    # ==========================================================

    with op.batch_alter_table(
        "sale_payments",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "currency_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "original_amount",
                sa.Numeric(
                    precision=15,
                    scale=2
                ),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "exchange_rate",
                sa.Numeric(
                    precision=20,
                    scale=8
                ),
                nullable=True
            )
        )

    # ==========================================================
    # 2. FIND UGX CURRENCY
    # ==========================================================

    connection = op.get_bind()

    ugx_id = connection.execute(
        sa.text(
            """
            SELECT id
            FROM currencies
            WHERE code = 'UGX'
            LIMIT 1
            """
        )
    ).scalar()

    if ugx_id is None:
        raise RuntimeError(
            "UGX currency does not exist. "
            "Seed currencies before upgrading."
        )

    # ==========================================================
    # 3. MIGRATE EXISTING PAYMENTS
    #
    # Existing payments were already stored in UGX.
    #
    # Therefore:
    #
    # currency_id     = UGX
    # original_amount = existing UGX amount
    # exchange_rate   = 1
    #
    # This preserves the exact financial value of every
    # existing payment.
    # ==========================================================

    connection.execute(
        sa.text(
            """
            UPDATE sale_payments
            SET
                currency_id = :ugx_id,
                original_amount = amount,
                exchange_rate = 1
            WHERE currency_id IS NULL
            """
        ),
        {
            "ugx_id": ugx_id
        }
    )

    # ==========================================================
    # 4. MAKE COLUMNS REQUIRED
    # ==========================================================

    with op.batch_alter_table(
        "sale_payments",
        schema=None
    ) as batch_op:

        batch_op.alter_column(
            "currency_id",
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.alter_column(
            "original_amount",
            existing_type=sa.Numeric(
                precision=15,
                scale=2
            ),
            nullable=False
        )

        batch_op.alter_column(
            "exchange_rate",
            existing_type=sa.Numeric(
                precision=20,
                scale=8
            ),
            nullable=False
        )

    # ==========================================================
    # 5. ADD FOREIGN KEY
    # ==========================================================

    with op.batch_alter_table(
        "sale_payments",
        schema=None
    ) as batch_op:

        batch_op.create_foreign_key(
            "fk_sale_payments_currency_id",
            "currencies",
            ["currency_id"],
            ["id"]
        )


def downgrade():

    with op.batch_alter_table(
        "sale_payments",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_sale_payments_currency_id",
            type_="foreignkey"
        )

        batch_op.drop_column(
            "exchange_rate"
        )

        batch_op.drop_column(
            "original_amount"
        )

        batch_op.drop_column(
            "currency_id"
        )