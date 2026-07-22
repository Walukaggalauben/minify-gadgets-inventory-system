from sqlalchemy import func
from datetime import date

from db import db

from models.product import Product
from models.product_variant import ProductVariant
from models.category import Category
from models.brand import Brand
from models.sale import Sale
from models.purchase import Purchase


class DashboardService:

    @staticmethod
    def get_statistics():

        today = date.today()

        total_products = Product.query.count()

        total_variants = ProductVariant.query.count()

        total_categories = Category.query.count()

        total_brands = Brand.query.count()

        inventory_value = db.session.query(
            func.sum(
                ProductVariant.buying_price *
                ProductVariant.quantity
            )
        ).scalar() or 0

        today_sales = db.session.query(
            func.sum(Sale.total_amount)
        ).filter(
            func.date(Sale.sale_date) == today
        ).scalar() or 0

        today_profit = db.session.query(
            func.sum(Sale.profit)
        ).filter(
            func.date(Sale.sale_date) == today
        ).scalar() or 0

        low_stock = ProductVariant.query.filter(
            ProductVariant.quantity <= ProductVariant.minimum_stock
        ).all()

        recent_sales = Sale.query.order_by(
            Sale.sale_date.desc()
        ).limit(5).all()

        recent_purchases = Purchase.query.order_by(
            Purchase.purchase_date.desc()
        ).limit(5).all()

        return {

            "total_products": total_products,

            "total_variants": total_variants,

            "total_categories": total_categories,

            "total_brands": total_brands,

            "inventory_value": inventory_value,

            "today_sales": today_sales,

            "today_profit": today_profit,

            "recent_sales": recent_sales,

            "recent_purchases": recent_purchases,

            "low_stock": low_stock

        }