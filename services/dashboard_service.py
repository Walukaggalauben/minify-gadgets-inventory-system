from datetime import date, timedelta

from sqlalchemy import func

from db import db

from models.brand import Brand
from models.category import Category
from models.imei import IMEI
from models.product import Product
from models.product_variant import ProductVariant
from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.sale import Sale
from models.sale_item import SaleItem
from models.supplier import Supplier
from models.system_setting import SystemSetting
from models.expense import Expense


class DashboardService:

    @staticmethod
    def get_statistics():

        today = date.today()

        settings = SystemSetting.get_settings()

        # Operating expenses and customer credit
        total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar() or 0
        outstanding_credit = db.session.query(func.coalesce(func.sum(Sale.balance_due), 0)).filter(Sale.balance_due > 0).scalar() or 0

        # ==================================================
        # BASIC COUNTS
        # ==================================================

        total_products = Product.query.count()
        total_variants = ProductVariant.query.count()
        total_categories = Category.query.count()
        total_brands = Brand.query.count()
        total_suppliers = Supplier.query.count()

        # ==================================================
        # INVENTORY
        # ==================================================

        available_stock = (
            db.session.query(func.sum(ProductVariant.quantity)).scalar() or 0
        )

        out_of_stock = ProductVariant.query.filter(ProductVariant.quantity == 0).count()

        if settings.enable_low_stock_alerts:
            low_stock = (
                db.session.query(
                    Brand.name.label("brand"),
                    Product.name.label("product"),
                    func.concat(
                        func.coalesce(ProductVariant.storage, ""),
                        " / ",
                        func.coalesce(ProductVariant.ram, ""),
                        " / ",
                        func.coalesce(ProductVariant.colour, ""),
                    ).label("variant"),
                    ProductVariant.quantity,
                )
                .join(Product, Product.id == ProductVariant.product_id)
                .join(Brand, Brand.id == Product.brand_id)
                .filter(ProductVariant.quantity <= ProductVariant.minimum_stock)
                .order_by(ProductVariant.quantity.asc())
                .all()
            )
        else:
            low_stock = []

        low_stock_count = len(low_stock)

        inventory_cost = (
            db.session.query(
                func.sum(ProductVariant.buying_price * ProductVariant.quantity)
            ).scalar()
            or 0
        )

        inventory_selling_value = (
            db.session.query(
                func.sum(ProductVariant.selling_price * ProductVariant.quantity)
            ).scalar()
            or 0
        )

        expected_profit = inventory_selling_value - inventory_cost

        average_buying_price = (
            db.session.query(func.avg(ProductVariant.buying_price)).scalar() or 0
        )

        average_selling_price = (
            db.session.query(func.avg(ProductVariant.selling_price)).scalar() or 0
        )

        # ==================================================
        # IMEI ANALYTICS
        # ==================================================

        total_imeis = IMEI.query.count()

        available_imeis = IMEI.query.filter(IMEI.status == "In Stock").count()

        reserved_imeis = IMEI.query.filter(IMEI.status == "Reserved").count()

        sold_imeis = IMEI.query.filter(IMEI.status == "Sold").count()

        damaged_imeis = IMEI.query.filter(IMEI.status == "Damaged").count()

        returned_imeis = IMEI.query.filter(IMEI.status == "Returned").count()

        # ==================================================
        # TODAY
        # ==================================================

        today_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(func.date(Sale.sale_date) == today)
            .scalar()
            or 0
        )

        today_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(func.date(Sale.sale_date) == today)
            .scalar()
            or 0
        )

        today_transactions = Sale.query.filter(
            func.date(Sale.sale_date) == today
        ).count()

        products_sold_today = (
            db.session.query(func.sum(SaleItem.quantity))
            .join(Sale)
            .filter(func.date(Sale.sale_date) == today)
            .scalar()
            or 0
        )

        purchases_today = (
            db.session.query(func.sum(Purchase.total_amount))
            .filter(Purchase.purchase_date == today)
            .scalar()
            or 0
        )

        # ==================================================
        # WEEK
        # ==================================================

        week_start = today - timedelta(days=today.weekday())

        week_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(func.date(Sale.sale_date) >= week_start)
            .scalar()
            or 0
        )

        week_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(func.date(Sale.sale_date) >= week_start)
            .scalar()
            or 0
        )

        week_purchases = (
            db.session.query(func.sum(Purchase.total_amount))
            .filter(Purchase.purchase_date >= week_start)
            .scalar()
            or 0
        )

        # ==================================================
        # MONTH
        # ==================================================

        month_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(
                func.extract("year", Sale.sale_date) == today.year,
                func.extract("month", Sale.sale_date) == today.month,
            )
            .scalar()
            or 0
        )

        month_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(
                func.extract("year", Sale.sale_date) == today.year,
                func.extract("month", Sale.sale_date) == today.month,
            )
            .scalar()
            or 0
        )

        month_purchases = (
            db.session.query(func.sum(Purchase.total_amount))
            .filter(
                func.extract("year", Purchase.purchase_date) == today.year,
                func.extract("month", Purchase.purchase_date) == today.month,
            )
            .scalar()
            or 0
        )

        # ==================================================
        # YEAR
        # ==================================================

        year_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(func.extract("year", Sale.sale_date) == today.year)
            .scalar()
            or 0
        )

        year_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(func.extract("year", Sale.sale_date) == today.year)
            .scalar()
            or 0
        )

        year_purchases = (
            db.session.query(func.sum(Purchase.total_amount))
            .filter(func.extract("year", Purchase.purchase_date) == today.year)
            .scalar()
            or 0
        )

        average_sale = db.session.query(func.avg(Sale.total_amount)).scalar() or 0

        # ==================================================
        # RECENT SALES
        # ==================================================

        recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(10).all()

        # ==================================================
        # RECENT PURCHASES
        # ==================================================

        recent_purchases = (
            Purchase.query.order_by(Purchase.purchase_date.desc()).limit(10).all()
        )

        # ==================================================
        # TOP SELLING PRODUCTS
        # ==================================================

        top_products = (
            db.session.query(
                Product.name.label("product"),
                func.sum(SaleItem.quantity).label("sold"),
                func.sum(SaleItem.total).label("sales"),
                func.sum(SaleItem.profit).label("profit"),
            )
            .join(ProductVariant, SaleItem.product_variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(10)
            .all()
        )

        # ==================================================
        # MOST PROFITABLE PRODUCTS
        # ==================================================

        profitable_products = (
            db.session.query(
                Product.name.label("product"), func.sum(SaleItem.profit).label("profit")
            )
            .join(ProductVariant, SaleItem.product_variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(SaleItem.profit).desc())
            .limit(10)
            .all()
        )

        # ==================================================
        # BRAND PERFORMANCE
        # ==================================================

        brand_performance = (
            db.session.query(
                Brand.name.label("brand"),
                func.sum(SaleItem.quantity).label("sold"),
                func.sum(SaleItem.total).label("sales"),
            )
            .join(Product, Brand.id == Product.brand_id)
            .join(ProductVariant, Product.id == ProductVariant.product_id)
            .join(SaleItem, ProductVariant.id == SaleItem.product_variant_id)
            .group_by(Brand.id, Brand.name)
            .order_by(func.sum(SaleItem.total).desc())
            .all()
        )

        # ==================================================
        # CATEGORY PERFORMANCE
        # ==================================================

        category_performance = (
            db.session.query(
                Category.name.label("category"),
                func.sum(SaleItem.quantity).label("sold"),
                func.sum(SaleItem.total).label("sales"),
            )
            .join(Product, Category.id == Product.category_id)
            .join(ProductVariant, Product.id == ProductVariant.product_id)
            .join(SaleItem, ProductVariant.id == SaleItem.product_variant_id)
            .group_by(Category.id, Category.name)
            .order_by(func.sum(SaleItem.total).desc())
            .all()
        )

        # ==================================================
        # INVENTORY STATUS
        # ==================================================

        inventory_status = {
            "available": available_imeis,
            "sold": sold_imeis,
            "reserved": reserved_imeis,
            "damaged": damaged_imeis,
            "returned": returned_imeis,
        }

        # ==================================================
        # SALES SUMMARY
        # ==================================================

        sales_summary = {
            "today": float(today_sales),
            "week": float(week_sales),
            "month": float(month_sales),
            "year": float(year_sales),
        }

        profit_summary = {
            "today": float(today_profit),
            "week": float(week_profit),
            "month": float(month_profit),
            "year": float(year_profit),
        }

        purchase_summary = {
            "today": float(purchases_today),
            "week": float(week_purchases),
            "month": float(month_purchases),
            "year": float(year_purchases),
        }

        # ==================================================
        # MONTHLY SALES VS PURCHASES (12 MONTHS)
        # ==================================================

        monthly_labels = []
        monthly_sales = []
        monthly_purchases = []

        for month in range(1, 13):

            sales_total = (
                db.session.query(func.sum(Sale.total_amount))
                .filter(
                    func.extract("year", Sale.sale_date) == today.year,
                    func.extract("month", Sale.sale_date) == month,
                )
                .scalar()
                or 0
            )

            purchase_total = (
                db.session.query(func.sum(Purchase.total_amount))
                .filter(
                    func.extract("year", Purchase.purchase_date) == today.year,
                    func.extract("month", Purchase.purchase_date) == month,
                )
                .scalar()
                or 0
            )

            monthly_labels.append(date(today.year, month, 1).strftime("%b"))

            monthly_sales.append(float(sales_total))
            monthly_purchases.append(float(purchase_total))

        # ==================================================
        # LAST 30 DAYS SALES / PROFIT
        # ==================================================

        chart_labels = []
        sales_values = []
        profit_values = []

        for i in range(29, -1, -1):

            current_day = today - timedelta(days=i)

            sales = (
                db.session.query(func.sum(Sale.total_amount))
                .filter(func.date(Sale.sale_date) == current_day)
                .scalar()
                or 0
            )

            profit = (
                db.session.query(func.sum(Sale.profit))
                .filter(func.date(Sale.sale_date) == current_day)
                .scalar()
                or 0
            )

            chart_labels.append(current_day.strftime("%d %b"))

            sales_values.append(float(sales))
            profit_values.append(float(profit))

        # ==================================================
        # TOP PRODUCT CHART
        # ==================================================

        top_product_labels = [p.product for p in top_products]

        top_product_sales = [float(p.sales or 0) for p in top_products]

        # ==================================================
        # BRAND CHART
        # ==================================================

        brand_labels = [b.brand for b in brand_performance]

        brand_sales = [float(b.sales or 0) for b in brand_performance]

        # ==================================================
        # CATEGORY CHART
        # ==================================================

        category_labels = [c.category for c in category_performance]

        category_sales = [float(c.sales or 0) for c in category_performance]

        # ==================================================
        # RETURN
        # ==================================================

        return {
            # -------------------------
            # BASIC COUNTS
            # -------------------------
            "total_products": total_products,
            "total_variants": total_variants,
            "total_categories": total_categories,
            "total_brands": total_brands,
            "total_suppliers": total_suppliers,
            # -------------------------
            # INVENTORY
            # -------------------------
            "available_stock": available_stock,
            "inventory_cost": inventory_cost,
            "inventory_value": inventory_selling_value,
            "expected_profit": expected_profit,
            "average_buying_price": average_buying_price,
            "average_selling_price": average_selling_price,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "low_stock_count": low_stock_count,
            # -------------------------
            # IMEI
            # -------------------------
            "total_imeis": total_imeis,
            "available_imeis": available_imeis,
            "reserved_imeis": reserved_imeis,
            "sold_imeis": sold_imeis,
            "damaged_imeis": damaged_imeis,
            "returned_imeis": returned_imeis,
            "inventory_status": inventory_status,
            # -------------------------
            # SALES
            # -------------------------
            "today_sales": today_sales,
            "today_profit": today_profit,
            "today_transactions": today_transactions,
            "products_sold_today": products_sold_today,
            "week_sales": week_sales,
            "week_profit": week_profit,
            "month_sales": month_sales,
            "month_profit": month_profit,
            "year_sales": year_sales,
            "year_profit": year_profit,
            "average_sale": average_sale,
            "total_expenses": total_expenses,
            "outstanding_credit": outstanding_credit,
            "net_profit_after_expenses": float(year_profit) - float(total_expenses),
            "sales_summary": sales_summary,
            "profit_summary": profit_summary,
            "purchase_summary": purchase_summary,
            # -------------------------
            # TABLES
            # -------------------------
            "recent_sales": recent_sales,
            "recent_purchases": recent_purchases,
            "top_products": top_products,
            "profitable_products": profitable_products,
            # -------------------------
            # PERFORMANCE
            # -------------------------
            "brand_performance": brand_performance,
            "category_performance": category_performance,
            # -------------------------
            # CHARTS
            # -------------------------
            "chart_labels": chart_labels,
            "sales_values": sales_values,
            "profit_values": profit_values,
            "monthly_labels": monthly_labels,
            "monthly_sales": monthly_sales,
            "monthly_purchases": monthly_purchases,
            "top_product_labels": top_product_labels,
            "top_product_sales": top_product_sales,
            "brand_labels": brand_labels,
            "brand_sales": brand_sales,
            "category_labels": category_labels,
            "category_sales": category_sales,
        }
