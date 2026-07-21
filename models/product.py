from db import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    brand_id = db.Column(
        db.Integer,
        db.ForeignKey("brands.id"),
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
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

    category = db.relationship(
        "Category",
        back_populates="products"
    )

    brand = db.relationship(
        "Brand",
        back_populates="products"
    )

    variants = db.relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Product {self.name}>"