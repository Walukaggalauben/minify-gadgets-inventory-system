from utils.timezone import utc_now_naive

from db import db


class CustomerCreditTransaction(db.Model):
    """Immutable audit entries for customer-credit settlement.

    Supported transaction types include REFUND, CREDIT_APPLIED, ADJUSTMENT,
    and CONVERTED_TO_INCOME. A conversion to income ends the customer's
    refundable credit and records the business decision in the audit trail.
    """

    __tablename__ = "customer_credit_transactions"

    id = db.Column(db.Integer, primary_key=True)

    credit_id = db.Column(
        db.Integer,
        db.ForeignKey("customer_credits.id"),
        nullable=False,
    )

    transaction_type = db.Column(
        db.String(30),
        nullable=False,
    )

    amount = db.Column(
        db.Numeric(15, 2),
        nullable=False,
    )

    payment_method = db.Column(
        db.String(30),
        nullable=True,
    )

    reference = db.Column(
        db.String(100),
        nullable=True,
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    processed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=utc_now_naive,
        nullable=False,
    )

    credit = db.relationship(
        "CustomerCredit",
        back_populates="transactions",
    )

    user = db.relationship(
        "User",
        foreign_keys=[processed_by],
        lazy="joined",
    )

    def __repr__(self):
        return f"<CustomerCreditTransaction {self.id} {self.transaction_type} {self.amount}>"
