from models.product import Product
from db import db


class ProductService:

    @staticmethod
    def get_all():
        return Product.query.order_by(Product.name).all()

    @staticmethod
    def get(product_id):
        return Product.query.get_or_404(product_id)

    @staticmethod
    def create(data):

        product = Product(
            category_id=data["category_id"],
            brand_id=data["brand_id"],
            name=data["name"],
            description=data.get("description"),
            image=data.get("image"),
            is_active=True
        )

        db.session.add(product)
        db.session.commit()

        return product

    @staticmethod
    def update(product, data):

        product.category_id = data["category_id"]
        product.brand_id = data["brand_id"]
        product.name = data["name"]
        product.description = data.get("description")
        product.image = data.get("image")

        db.session.commit()
        return product

    @staticmethod
    def toggle_status(product):

        product.is_active = not product.is_active

        db.session.commit()