from datetime import datetime
from db import db


class SalePayment(db.Model):
    __tablename__ = "sale_payments"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False, default="Cash")
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    received_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    sale = db.relationship("Sale", back_populates="payments")
    user = db.relationship("User", foreign_keys=[received_by])

    def __repr__(self):
        return f"<SalePayment {self.id}>"
