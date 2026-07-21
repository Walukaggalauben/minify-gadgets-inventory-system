from db import db
from models.product_variant import ProductVariant


class ProductVariantService:

    @staticmethod
    def get_all():
        return ProductVariant.query.order_by(
            ProductVariant.product_id,
            ProductVariant.storage,
            ProductVariant.ram
        ).all()

    @staticmethod
    def get(variant_id):
        return ProductVariant.query.get_or_404(variant_id)

    @staticmethod
    def create(data):

        variant = ProductVariant(
            product_id=data["product_id"],
            sku=data["sku"],
            barcode=data.get("barcode"),
            storage=data.get("storage"),
            ram=data.get("ram"),
            colour=data.get("colour"),
            condition=data.get("condition"),
            buying_price=data["buying_price"],
            selling_price=data["selling_price"],
            quantity=data["quantity"],
            minimum_stock=data.get("minimum_stock", 1),
            warranty_months=data.get("warranty_months", 12),
            image=data.get("image"),
            is_active=True
        )

        db.session.add(variant)
        db.session.commit()

        return variant

    @staticmethod
    def update(variant, data):

        variant.product_id = data["product_id"]
        variant.sku = data["sku"]
        variant.barcode = data.get("barcode")
        variant.storage = data.get("storage")
        variant.ram = data.get("ram")
        variant.colour = data.get("colour")
        variant.condition = data.get("condition")
        variant.buying_price = data["buying_price"]
        variant.selling_price = data["selling_price"]
        variant.quantity = data["quantity"]
        variant.minimum_stock = data.get("minimum_stock", 1)
        variant.warranty_months = data.get("warranty_months", 12)
        variant.image = data.get("image")

        db.session.commit()

        return variant

    @staticmethod
    def toggle_status(variant):

        variant.is_active = not variant.is_active

        db.session.commit()