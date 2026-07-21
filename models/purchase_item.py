from db import db


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id"),
        nullable=False
    )

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_cost = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    subtotal = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    purchase = db.relationship(
        "Purchase",
        back_populates="items"
    )

    product_variant = db.relationship(
        "ProductVariant",
        back_populates="purchase_items"
    )

    def __repr__(self):
        return f"<PurchaseItem {self.id}>"