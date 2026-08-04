"""Move buying price to IMEI

Revision ID: 4051c1b71b71
Revises: 7fa3586f81a9
Create Date: 2026-07-29 14:39:32.713974
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "4051c1b71b71"
down_revision = "7fa3586f81a9"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("imeis", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "buying_price",
                sa.Numeric(15, 2),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "default_selling_price",
                sa.Numeric(15, 2),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "acquisition_source",
                sa.Enum(
                    "Purchase",
                    "Trade In",
                    "Opening Stock",
                    "Adjustment",
                    "Return",
                    name="imei_acquisition_source",
                ),
                nullable=False,
                server_default="Purchase",
            )
        )

        batch_op.add_column(
            sa.Column(
                "received_date",
                sa.DateTime(),
                nullable=True,
                server_default=sa.func.now(),
            )
        )


def downgrade():

    with op.batch_alter_table("imeis", schema=None) as batch_op:

        batch_op.drop_column("received_date")

        batch_op.drop_column("acquisition_source")

        batch_op.drop_column("default_selling_price")

        batch_op.drop_column("buying_price")
