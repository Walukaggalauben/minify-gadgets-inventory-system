from datetime import datetime
from db import db


class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    invoice_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    customer_name = db.Column(
        db.String(150),
        nullable=False
    )

    customer_phone = db.Column(
        db.String(30)
    )

    total_amount = db.Column(
        db.Numeric(15, 2),
        default=0
    )

    profit = db.Column(
        db.Numeric(15, 2),
        default=0
    )

    payment_method = db.Column(
        db.String(30),
        default="Cash"
    )

    status = db.Column(
        db.String(20),
        default="Completed"
    )

    sale_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="sales"
    )

    items = db.relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Sale {self.invoice_number}>"