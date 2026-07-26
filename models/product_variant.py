from db import db


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    sku = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    barcode = db.Column(
        db.String(100),
        unique=True
    )

    storage = db.Column(
        db.String(50)
    )

    ram = db.Column(
        db.String(50)
    )

    colour = db.Column(
        db.String(50)
    )

    condition = db.Column(
        db.Enum(
            "Brand New",
            "Refurbished",
            "Used Grade A",
            "Used Grade B",
            name="product_condition"
        ),
        nullable=False,
        default="Brand New"
    )

    buying_price = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    selling_price = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    minimum_stock = db.Column(
        db.Integer,
        default=1
    )

    warranty_months = db.Column(
        db.Integer,
        default=12
    )

    image = db.Column(
        db.String(255)
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    product = db.relationship(
        "Product",
        back_populates="variants"
    )
    
    imeis = db.relationship(
    "IMEI",
    back_populates="product_variant",
    cascade="all, delete-orphan",
    lazy=True
    )
    
    purchase_items = db.relationship(
    "PurchaseItem",
    back_populates="product_variant",
    lazy=True
    )
    
    sale_items = db.relationship(
    "SaleItem",
    back_populates="product_variant",
    lazy=True
)

    def __repr__(self):
        return f"<Variant {self.sku}>"