from utils.timezone import utc_now_naive

from db import db


class CustomerCredit(db.Model):
    """Tracks money received above a sale's value.

    This is customer money, not sales revenue or profit. The original
    payment remains in SalePayment; this ledger tracks the excess separately.
    """

    __tablename__ = "customer_credits"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=True,
    )

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.id"),
        nullable=False,
        unique=True,
    )

    original_amount = db.Column(
        db.Numeric(15, 2),
        nullable=False,
        default=0,
    )

    remaining_amount = db.Column(
        db.Numeric(15, 2),
        nullable=False,
        default=0,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Outstanding",
    )

    created_at = db.Column(
        db.DateTime,
        default=utc_now_naive,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
        nullable=False,
    )

    customer = db.relationship(
        "Customer",
        foreign_keys=[customer_id],
        lazy="joined",
    )

    sale = db.relationship(
        "Sale",
        foreign_keys=[sale_id],
        lazy="joined",
    )

    transactions = db.relationship(
        "CustomerCreditTransaction",
        back_populates="credit",
        cascade="all, delete-orphan",
        order_by="CustomerCreditTransaction.created_at.desc()",
        lazy=True,
    )

    def __repr__(self):
        return f"<CustomerCredit {self.id} sale={self.sale_id} remaining={self.remaining_amount}>"
