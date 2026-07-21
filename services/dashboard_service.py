from sqlalchemy import func

from db import db

from models.product import Product
from models.product_variant import ProductVariant
from models.category import Category
from models.brand import Brand


class DashboardService:

    @staticmethod
    def get_statistics():

        total_products = Product.query.count()

        total_variants = ProductVariant.query.count()

        total_categories = Category.query.count()

        total_brands = Brand.query.count()

        stock_value = db.session.query(

            func.sum(
                ProductVariant.buying_price *
                ProductVariant.quantity
            )

        ).scalar() or 0

        low_stock = ProductVariant.query.filter(

            ProductVariant.quantity <= ProductVariant.minimum_stock

        ).count()

        out_of_stock = ProductVariant.query.filter(

            ProductVariant.quantity == 0

        ).count()

        return {

            "products": total_products,

            "variants": total_variants,

            "categories": total_categories,

            "brands": total_brands,

            "stock_value": stock_value,

            "low_stock": low_stock,

            "out_of_stock": out_of_stock

        }