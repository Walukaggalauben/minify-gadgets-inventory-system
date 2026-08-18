from db import db


class IMEI(db.Model):
    __tablename__ = "imeis"

    id = db.Column(db.Integer, primary_key=True)

    # ==================================================
    # PRODUCT
    # ==================================================

    product_variant_id = db.Column(
        db.Integer, db.ForeignKey("product_variants.id"), nullable=False
    )

    imei = db.Column(db.String(30), unique=True, nullable=False)

    serial_number = db.Column(db.String(100), unique=True)

    # ==================================================
    # PURCHASE / ACQUISITION TRACEABILITY
    # ==================================================

    # Nullable because existing IMEIs were created before
    # purchase-level traceability was introduced.
    purchase_item_id = db.Column(
        db.Integer, db.ForeignKey("purchase_items.id"), nullable=True
    )

    # ==================================================
    # STOCK STATUS
    # ==================================================

    status = db.Column(
        db.Enum(
            "In Stock", "Reserved", "Sold", "Returned", "Damaged", name="imei_status"
        ),
        nullable=False,
        default="In Stock",
    )

    # ==================================================
    # COSTING
    # ==================================================

    buying_price = db.Column(db.Numeric(15, 2), nullable=True)

    default_selling_price = db.Column(db.Numeric(15, 2), nullable=True)

    acquisition_source = db.Column(
        db.Enum(
            "Purchase",
            "Trade In",
            "Opening Stock",
            "Adjustment",
            "Return",
            name="imei_acquisition_source",
        ),
        default="Purchase",
        nullable=False,
    )

    received_date = db.Column(db.DateTime, server_default=db.func.now())

    # ==================================================
    # NOTES
    # ==================================================

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    product_variant = db.relationship("ProductVariant", back_populates="imeis")

    # Original purchase item that created this physical unit.
    purchase_item = db.relationship("PurchaseItem", back_populates="imeis")

    sale_items = db.relationship("SaleItem", back_populates="imei", lazy=True)

    trade_in_item = db.relationship("TradeInItem", back_populates="imei", uselist=False)

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
    # PURCHASE TRACE HELPERS
    # ==================================================

    @property
    def purchase(self):
        """
        Return the purchase that originally received this IMEI.
        Existing historical IMEIs may return None because they
        predate purchase-item traceability.
        """
        if self.purchase_item:
            return self.purchase_item.purchase

        return None

    @property
    def supplier(self):
        """
        Return the supplier from the original purchase.
        """
        purchase = self.purchase

        if purchase:
            return purchase.supplier

        return None

    @property
    def purchase_number(self):
        """
        Return the original purchase number where available.
        """
        purchase = self.purchase

        if purchase:
            return purchase.purchase_number

        return None

    # ==================================================
    # REPRESENTATION
    # ==================================================

    def __repr__(self):
        return f"<IMEI {self.imei}>"
