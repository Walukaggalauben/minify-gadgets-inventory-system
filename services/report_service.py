from datetime import datetime, time
from db import db
from sqlalchemy import func

from models.sale import Sale
from models.sale_item import SaleItem
from models.product_variant import ProductVariant
from models.purchase import Purchase
from models.imei import IMEI
from models.customer_credit_transaction import CustomerCreditTransaction


class ReportService:
    """
    Central reporting service.

    All reports should obtain their data from here instead of querying
    the database directly in the routes.
    """

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    @staticmethod
    def _parse_dates(start_date, end_date):
        """
        Convert YYYY-MM-DD strings into datetime objects.
        """

        start = None
        end = None

        if start_date:
            start = datetime.combine(
                datetime.strptime(start_date, "%Y-%m-%d").date(), time.min
            )

        if end_date:
            end = datetime.combine(
                datetime.strptime(end_date, "%Y-%m-%d").date(), time.max
            )

        return start, end

    @staticmethod
    def _credit_summary(start=None, end=None):
        """Return converted customer-credit income and refunds for a period."""
        income_query = db.session.query(
            func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
        ).filter(CustomerCreditTransaction.transaction_type == "CONVERTED_TO_INCOME")

        refund_query = db.session.query(
            func.coalesce(func.sum(CustomerCreditTransaction.amount), 0)
        ).filter(CustomerCreditTransaction.transaction_type == "REFUND")

        if start:
            income_query = income_query.filter(
                CustomerCreditTransaction.created_at >= start
            )
            refund_query = refund_query.filter(
                CustomerCreditTransaction.created_at >= start
            )

        if end:
            income_query = income_query.filter(
                CustomerCreditTransaction.created_at <= end
            )
            refund_query = refund_query.filter(
                CustomerCreditTransaction.created_at <= end
            )

        converted_income = income_query.scalar() or 0
        refunds = refund_query.scalar() or 0

        return float(converted_income), float(refunds)

    # ----------------------------------------------------
    # SALES REPORT
    # ----------------------------------------------------

    @classmethod
    def sales_report(cls, start_date=None, end_date=None):

        start, end = cls._parse_dates(start_date, end_date)

        query = Sale.query.filter(Sale.status != "Cancelled").order_by(
            Sale.sale_date.desc()
        )

        if start:
            query = query.filter(Sale.sale_date >= start)

        if end:
            query = query.filter(Sale.sale_date <= end)

        sales = query.all()

        converted_credit_income, customer_credit_refunds = cls._credit_summary(
            start, end
        )

        sale_profit = float(sum(float(s.profit or 0) for s in sales))

        business_profit = (
            sale_profit + converted_credit_income - customer_credit_refunds
        )

        summary = {
            "invoice_count": len(sales),
            "total_sales": float(sum(float(s.total_amount or 0) for s in sales)),
            "sale_profit": sale_profit,
            "converted_credit_income": converted_credit_income,
            "customer_credit_refunds": customer_credit_refunds,
            "total_profit": business_profit,
        }

        return sales, summary

        # ----------------------------------------------------

    # REPORT DASHBOARD
    # ----------------------------------------------------

    @classmethod
    def dashboard_summary(cls):

        sales = Sale.query.filter(Sale.status != "Cancelled").all()
        variants = ProductVariant.query.all()

        total_sales = len(sales)

        total_revenue = sum(float(s.total_amount or 0) for s in sales)

        sale_profit = sum(float(s.profit or 0) for s in sales)

        converted_credit_income, customer_credit_refunds = cls._credit_summary()

        total_profit = sale_profit + converted_credit_income - customer_credit_refunds

        inventory_value = sum(float(v.buying_price) * v.quantity for v in variants)

        total_products = len(variants)

        total_purchases = Purchase.query.count()

        low_stock = sum(1 for v in variants if v.quantity <= v.minimum_stock)

        recent_sales = (
            Sale.query.filter(Sale.status != "Cancelled")
            .order_by(Sale.sale_date.desc())
            .limit(10)
            .all()
        )

        low_stock_products = (
            ProductVariant.query.filter(
                ProductVariant.quantity <= ProductVariant.minimum_stock
            )
            .order_by(ProductVariant.quantity.asc())
            .limit(10)
            .all()
        )

        return {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "sale_profit": sale_profit,
            "converted_credit_income": converted_credit_income,
            "customer_credit_refunds": customer_credit_refunds,
            "total_profit": total_profit,
            "inventory_value": inventory_value,
            "total_products": total_products,
            "total_purchases": total_purchases,
            "low_stock": low_stock,
            "recent_sales": recent_sales,
            "low_stock_products": low_stock_products,
        }

    # ----------------------------------------------------
    # INVENTORY REPORT
    # ----------------------------------------------------

    @classmethod
    def inventory_report(cls):

        variants = ProductVariant.query.order_by(ProductVariant.created_at.desc()).all()

        total_stock = sum(v.quantity for v in variants)

        stock_value = sum(float(v.buying_price) * v.quantity for v in variants)

        selling_value = sum(float(v.selling_price) * v.quantity for v in variants)

        expected_profit = selling_value - stock_value

        summary = {
            "products": len(variants),
            "stock": total_stock,
            "cost_value": stock_value,
            "selling_value": selling_value,
            "expected_profit": expected_profit,
        }

        return variants, summary

    # ----------------------------------------------------
    # LOW STOCK REPORT
    # ----------------------------------------------------

    @classmethod
    def low_stock_report(cls):

        products = (
            ProductVariant.query.filter(
                ProductVariant.quantity <= ProductVariant.minimum_stock
            )
            .order_by(ProductVariant.quantity.asc())
            .all()
        )

        return products

    # ----------------------------------------------------
    # PURCHASE REPORT
    # ----------------------------------------------------

    @classmethod
    def purchase_report(cls, start_date=None, end_date=None):

        start, end = cls._parse_dates(start_date, end_date)

        query = Purchase.query

        if start:
            query = query.filter(Purchase.purchase_date >= start)

        if end:
            query = query.filter(Purchase.purchase_date <= end)

        purchases = query.order_by(Purchase.purchase_date.desc()).all()

        total = sum(float(getattr(p, "total_amount", 0) or 0) for p in purchases)

        summary = {"count": len(purchases), "total": total}

        return purchases, summary

    # ----------------------------------------------------
    # IMEI REPORT
    # ----------------------------------------------------

    @classmethod
    def imei_report(cls):

        imeis = IMEI.query.order_by(IMEI.created_at.desc()).all()

        return imeis

    # ----------------------------------------------------
    # PROFIT REPORT
    # ----------------------------------------------------

    @classmethod
    def profit_report(cls, start_date=None, end_date=None):

        sales, _ = cls.sales_report(start_date, end_date)

        sale_profit = sum(float(s.profit or 0) for s in sales)

        converted_credit_income, customer_credit_refunds = cls._credit_summary(
            *cls._parse_dates(start_date, end_date)
        )

        total_profit = sale_profit + converted_credit_income - customer_credit_refunds

        average_profit = total_profit / len(sales) if sales else 0

        summary = {
            "sales": len(sales),
            "sale_profit": sale_profit,
            "converted_credit_income": converted_credit_income,
            "customer_credit_refunds": customer_credit_refunds,
            "profit": total_profit,
            "average_profit": average_profit,
        }

        return sales, summary
