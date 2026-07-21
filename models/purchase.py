from datetime import datetime
from db import db


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)

    purchase_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id"),
        nullable=False
    )

    purchase_date = db.Column(
        db.Date,
        nullable=False
    )

    invoice_number = db.Column(
        db.String(100),
        nullable=True
    )

    payment_method = db.Column(
        db.String(50),
        nullable=True
    )

    total_amount = db.Column(
        db.Numeric(12, 2),
        default=0
    )

    status = db.Column(
        db.String(20),
        default="Draft"
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    supplier = db.relationship(
        "Supplier",
        back_populates="purchases"
    )

    user = db.relationship(
        "User",
        back_populates="purchases"
    )

    items = db.relationship(
        "PurchaseItem",
        back_populates="purchase",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Purchase {self.purchase_number}>"