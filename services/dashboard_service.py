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
from models.customer_credit_transaction import CustomerCreditTransaction

from utils.timezone import application_date


class DashboardService:

    @staticmethod
    def get_statistics():

        today = application_date()

        # Week starts on Monday.
        week_start = today - timedelta(days=today.weekday())

        settings = SystemSetting.get_settings()

        # ==================================================
        # CUSTOMER CREDIT / OTHER BUSINESS INCOME
        # ==================================================
        # Customer overpayments are NOT part of Sale.profit.
        # Only credits explicitly converted to business income
        # become additional business income. Refunds are deducted.
        converted_credit_income = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME")
            .scalar()
            or 0
        )

        customer_credit_refunds = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(CustomerCreditTransaction.transaction_type == "REFUND")
            .scalar()
            or 0
        )

        # Operating expenses and customer credit
        total_expenses = (
            db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar() or 0
        )

        year_expenses = (
            db.session.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(func.extract("year", Expense.expense_date) == today.year)
            .scalar()
            or 0
        )

        outstanding_credit = (
            db.session.query(func.coalesce(func.sum(Sale.balance_due), 0))
            .filter(Sale.balance_due > 0)
            .scalar()
            or 0
        )

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
        # CUSTOMER CREDIT - PERIOD BREAKDOWNS
        # ==================================================

        today_credit_income = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME",
                func.date(CustomerCreditTransaction.created_at) == today,
            )
            .scalar()
            or 0
        )

        today_credit_refunds = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "REFUND",
                func.date(CustomerCreditTransaction.created_at) == today,
            )
            .scalar()
            or 0
        )

        # ==================================================
        # TODAY
        # ==================================================

        today_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(
                func.date(Sale.sale_date) == today,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        today_sale_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(
                func.date(Sale.sale_date) == today,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        today_profit = (
            float(today_sale_profit)
            + float(today_credit_income)
        )

        today_transactions = Sale.query.filter(
            func.date(Sale.sale_date) == today,
            Sale.status != "Cancelled",
        ).count()

        products_sold_today = (
            db.session.query(func.sum(SaleItem.quantity))
            .join(Sale)
            .filter(
                func.date(Sale.sale_date) == today,
                Sale.status != "Cancelled",
            )
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

        # Calculate the week boundary BEFORE any week-based queries use it.
        # Monday is the first day of the week.

        # ==================================================
        # WEEK - CUSTOMER CREDIT
        # ==================================================

        week_credit_income = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME",
                func.date(CustomerCreditTransaction.created_at) >= week_start,
            )
            .scalar()
            or 0
        )

        week_credit_refunds = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "REFUND",
                func.date(CustomerCreditTransaction.created_at) >= week_start,
            )
            .scalar()
            or 0
        )

        # ==================================================
        # WEEK SALES / PURCHASES
        # ==================================================

        week_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(
                func.date(Sale.sale_date) >= week_start,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        week_sale_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(
                func.date(Sale.sale_date) >= week_start,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        week_profit = (
            float(week_sale_profit)
            + float(week_credit_income)
        )

        week_purchases = (
            db.session.query(func.sum(Purchase.total_amount))
            .filter(Purchase.purchase_date >= week_start)
            .scalar()
            or 0
        )

        # ==================================================
        # MONTH - CUSTOMER CREDIT
        # ==================================================

        month_credit_income = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME",
                func.extract("year", CustomerCreditTransaction.created_at)
                == today.year,
                func.extract("month", CustomerCreditTransaction.created_at)
                == today.month,
            )
            .scalar()
            or 0
        )

        month_credit_refunds = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "REFUND",
                func.extract("year", CustomerCreditTransaction.created_at)
                == today.year,
                func.extract("month", CustomerCreditTransaction.created_at)
                == today.month,
            )
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
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        month_sale_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(
                func.extract("year", Sale.sale_date) == today.year,
                func.extract("month", Sale.sale_date) == today.month,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        month_profit = (
            float(month_sale_profit)
            + float(month_credit_income)
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
        # YEAR - CUSTOMER CREDIT
        # ==================================================

        year_credit_income = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME",
                func.extract("year", CustomerCreditTransaction.created_at)
                == today.year,
            )
            .scalar()
            or 0
        )

        year_credit_refunds = (
            db.session.query(
                func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
            )
            .filter(
                CustomerCreditTransaction.transaction_type == "REFUND",
                func.extract("year", CustomerCreditTransaction.created_at)
                == today.year,
            )
            .scalar()
            or 0
        )

        # ==================================================
        # YEAR
        # ==================================================

        year_sales = (
            db.session.query(func.sum(Sale.total_amount))
            .filter(
                func.extract("year", Sale.sale_date) == today.year,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        year_sale_profit = (
            db.session.query(func.sum(Sale.profit))
            .filter(
                func.extract("year", Sale.sale_date) == today.year,
                Sale.status != "Cancelled",
            )
            .scalar()
            or 0
        )

        year_profit = (
            float(year_sale_profit)
            + float(year_credit_income)
        )

        year_purchases = (
            db.session.query(func.sum(Purchase.total_amount))
            .filter(func.extract("year", Purchase.purchase_date) == today.year)
            .scalar()
            or 0
        )

        average_sale = (
            db.session.query(func.avg(Sale.total_amount))
            .filter(Sale.status != "Cancelled")
            .scalar()
            or 0
        )

        # ==================================================
        # RECENT SALES
        # ==================================================

        recent_sales = (
            Sale.query.filter(Sale.status != "Cancelled")
            .order_by(Sale.sale_date.desc())
            .limit(10)
            .all()
        )

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
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.status != "Cancelled")
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
                Product.name.label("product"),
                func.sum(SaleItem.profit).label("profit"),
            )
            .join(ProductVariant, SaleItem.product_variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.status != "Cancelled")
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
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.status != "Cancelled")
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
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.status != "Cancelled")
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
                    Sale.status != "Cancelled",
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

            sale_profit = (
                db.session.query(func.sum(Sale.profit))
                .filter(func.date(Sale.sale_date) == current_day)
                .scalar()
                or 0
            )

            credit_income = (
                db.session.query(
                    func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
                )
                .filter(
                    CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME",
                    func.date(CustomerCreditTransaction.created_at) == current_day,
                )
                .scalar()
                or 0
            )

            credit_refunds = (
                db.session.query(
                    func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
                )
                .filter(
                    CustomerCreditTransaction.transaction_type == "REFUND",
                    func.date(CustomerCreditTransaction.created_at) == current_day,
                )
                .scalar()
                or 0
            )

            profit = float(sale_profit) + float(credit_income) - float(credit_refunds)

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
            "today_sale_profit": float(today_sale_profit),
            "today_credit_income": float(today_credit_income),
            "today_credit_refunds": float(today_credit_refunds),
            "today_transactions": today_transactions,
            "products_sold_today": products_sold_today,
            "week_sales": week_sales,
            "week_profit": week_profit,
            "week_sale_profit": float(week_sale_profit),
            "week_credit_income": float(week_credit_income),
            "week_credit_refunds": float(week_credit_refunds),
            "month_sales": month_sales,
            "month_profit": month_profit,
            "month_sale_profit": float(month_sale_profit),
            "month_credit_income": float(month_credit_income),
            "month_credit_refunds": float(month_credit_refunds),
            "year_sales": year_sales,
            "year_profit": year_profit,
            "year_sale_profit": float(year_sale_profit),
            "year_credit_income": float(year_credit_income),
            "year_credit_refunds": float(year_credit_refunds),
            "average_sale": average_sale,
            "total_expenses": total_expenses,
            "year_expenses": year_expenses,
            "outstanding_credit": outstanding_credit,
            "converted_credit_income": float(converted_credit_income),
            "customer_credit_refunds": float(customer_credit_refunds),
            "net_profit_after_expenses": float(year_profit) - float(year_expenses),
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
