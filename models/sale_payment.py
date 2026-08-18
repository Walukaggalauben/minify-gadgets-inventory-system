from utils.timezone import utc_now_naive

from db import db


class SalePayment(db.Model):

    __tablename__ = "sale_payments"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)

    # ==========================================
    # PAYMENT AMOUNT
    # ==========================================

    # Always stored in the system/base currency (UGX).
    amount = db.Column(db.Numeric(15, 2), nullable=False)

    # ==========================================
    # FOREIGN CURRENCY DETAILS
    # ==========================================

    currency_id = db.Column(db.Integer, db.ForeignKey("currencies.id"), nullable=False)

    # Amount actually received from the customer
    # in the selected currency.
    original_amount = db.Column(db.Numeric(15, 2), nullable=False)

    # Conversion rate:
    # 1 selected currency = X UGX
    exchange_rate = db.Column(db.Numeric(20, 8), nullable=False, default=1)

    currency = db.relationship("Currency", foreign_keys=[currency_id], lazy="joined")

    # ==========================================
    # PAYMENT DETAILS
    # ==========================================

    payment_method = db.Column(db.String(30), nullable=False, default="Cash")

    payment_date = db.Column(db.DateTime, default=utc_now_naive, nullable=False)

    reference = db.Column(db.String(100))

    notes = db.Column(db.Text)

    received_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ==========================================
    # RELATIONSHIPS
    # ==========================================

    sale = db.relationship("Sale", back_populates="payments")

    user = db.relationship("User", foreign_keys=[received_by])

    # ==========================================
    # REPRESENTATION
    # ==========================================

    def __repr__(self):

        return f"<SalePayment {self.id}>"
