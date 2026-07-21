from db import db


class IMEI(db.Model):
    __tablename__ = "imeis"

    id = db.Column(db.Integer, primary_key=True)

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id"),
        nullable=False
    )

    imei = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    serial_number = db.Column(
        db.String(100),
        unique=True
    )

    status = db.Column(
        db.Enum(
            "In Stock",
            "Reserved",
            "Sold",
            "Returned",
            "Damaged",
            name="imei_status"
        ),
        nullable=False,
        default="In Stock"
    )

    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    product_variant = db.relationship(
        "ProductVariant",
        back_populates="imeis"
    )

    def __repr__(self):
        return f"<IMEI {self.imei}>"