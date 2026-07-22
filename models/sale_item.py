from db import db


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.id"),
        nullable=False
    )

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id"),
        nullable=False
    )

    imei_id = db.Column(
        db.Integer,
        db.ForeignKey("imeis.id"),
        nullable=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    selling_price = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    buying_price = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    total = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    profit = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    sale = db.relationship(
        "Sale",
        back_populates="items"
    )

    product_variant = db.relationship(
        "ProductVariant"
    )

    imei = db.relationship(
    "IMEI"
    )