from db import db


class IMEI(db.Model):
    __tablename__ = "imeis"

    id = db.Column(db.Integer, primary_key=True)

    # ==================================================
    # PRODUCT
    # ==================================================

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

    # ==================================================
    # STOCK STATUS
    # ==================================================

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

    # ==================================================
    # COSTING (NEW)
    # ==================================================

    buying_price = db.Column(
        db.Numeric(15, 2),
        nullable=True
    )

    default_selling_price = db.Column(
        db.Numeric(15, 2),
        nullable=True
    )

    acquisition_source = db.Column(
        db.Enum(
            "Purchase",
            "Trade In",
            "Opening Stock",
            "Adjustment",
            "Return",
            name="imei_acquisition_source"
        ),
        default="Purchase",
        nullable=False
    )

    received_date = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==================================================
    # NOTES
    # ==================================================

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

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    product_variant = db.relationship(
        "ProductVariant",
        back_populates="imeis"
    )

    sale_items = db.relationship(
        "SaleItem",
        back_populates="imei",
        lazy=True
    )
    
    trade_in_item = db.relationship(
    "TradeInItem",
    back_populates="imei",
    uselist=False
)

    # ==================================================
    # HELPER PROPERTIES
    # ==================================================

    @property
    def is_available(self):
        return self.status == "In Stock"

    @property
    def display_name(self):
        if self.product_variant:
            return (
                f"{self.product_variant.product.brand.name} "
                f"{self.product_variant.product.name} "
                f"{self.product_variant.storage} "
                f"{self.product_variant.colour}"
            )

        return self.imei

    # ==================================================
    # REPRESENTATION
    # ==================================================

    def __repr__(self):
        return f"<IMEI {self.imei}>"