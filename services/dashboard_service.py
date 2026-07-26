from datetime import date, timedelta

from sqlalchemy import func

from db import db

from models.product import Product
from models.product_variant import ProductVariant
from models.category import Category
from models.brand import Brand
from models.sale import Sale
from models.sale_item import SaleItem
from models.purchase import Purchase


class DashboardService:

    @staticmethod
    def get_statistics():

        today = date.today()

        # -----------------------------
        # Basic Counts
        # -----------------------------
        total_products = Product.query.count()

        total_variants = ProductVariant.query.count()

        total_categories = Category.query.count()

        total_brands = Brand.query.count()

        # -----------------------------
        # Inventory
        # -----------------------------
        available_stock = db.session.query(
            func.sum(ProductVariant.quantity)
        ).scalar() or 0

        inventory_value = db.session.query(
            func.sum(
                ProductVariant.buying_price *
                ProductVariant.quantity
            )
        ).scalar() or 0

        out_of_stock = ProductVariant.query.filter(
            ProductVariant.quantity == 0
        ).count()

        low_stock = ProductVariant.query.filter(
            ProductVariant.quantity <= ProductVariant.minimum_stock
        ).order_by(ProductVariant.quantity.asc()).all()

        low_stock_count = len(low_stock)

        # -----------------------------
        # Today's Performance
        # -----------------------------
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

        # -----------------------------
        # Monthly Performance
        # -----------------------------
        month_sales = db.session.query(
            func.sum(Sale.total_amount)
        ).filter(
            func.extract("year", Sale.sale_date) == today.year,
            func.extract("month", Sale.sale_date) == today.month
        ).scalar() or 0

        month_profit = db.session.query(
            func.sum(Sale.profit)
        ).filter(
            func.extract("year", Sale.sale_date) == today.year,
            func.extract("month", Sale.sale_date) == today.month
        ).scalar() or 0

        # -----------------------------
        # Recent Sales
        # -----------------------------
        recent_sales = (
            Sale.query
            .order_by(Sale.sale_date.desc())
            .limit(5)
            .all()
        )

        # -----------------------------
        # Recent Purchases
        # -----------------------------
        recent_purchases = (
            Purchase.query
            .order_by(Purchase.purchase_date.desc())
            .limit(5)
            .all()
        )

        # -----------------------------
        # Top Selling Products
        # -----------------------------
        top_products = (
            db.session.query(
                Product.name.label("product"),
                func.sum(SaleItem.quantity).label("sold")
            )
            .join(
                ProductVariant,
                SaleItem.product_variant_id == ProductVariant.id
            )
            .join(
                Product,
                ProductVariant.product_id == Product.id
            )
            .group_by(Product.id, Product.name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(5)
            .all()
        )

        # -----------------------------
        # Last 30 Days Sales
        # -----------------------------
        chart_labels = []
        chart_values = []

        for i in range(29, -1, -1):

            current_day = today - timedelta(days=i)

            total = db.session.query(
                func.sum(Sale.total_amount)
            ).filter(
                func.date(Sale.sale_date) == current_day
            ).scalar() or 0

            chart_labels.append(
                current_day.strftime("%d %b")
            )

            chart_values.append(float(total))

        return {

            # Counts
            "total_products": total_products,
            "total_variants": total_variants,
            "total_categories": total_categories,
            "total_brands": total_brands,

            # Inventory
            "available_stock": available_stock,
            "inventory_value": inventory_value,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "low_stock_count": low_stock_count,

            # Daily
            "today_sales": today_sales,
            "today_profit": today_profit,

            # Monthly
            "month_sales": month_sales,
            "month_profit": month_profit,

            # Tables
            "recent_sales": recent_sales,
            "recent_purchases": recent_purchases,
            "top_products": top_products,

            # Charts
            "chart_labels": chart_labels,
            "chart_values": chart_values

        }