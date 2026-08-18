import json

from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)

from db import db

from models.product_variant import ProductVariant
from models.imei import IMEI
from models.brand import Brand
from models.product import Product
from models.customer import Customer
from models.sale import Sale
from models.company import Company
from models.system_setting import SystemSetting
from models.sale_payment import SalePayment
from models.currency import Currency
from models.customer_credit import CustomerCredit
from models.customer_credit_transaction import CustomerCreditTransaction

from services.sale_service import SaleService
from services.currency_service import CurrencyService


sale_bp = Blueprint(
    "sale",
    __name__,
    url_prefix="/sales",
)


# ==========================================================
# SALES LIST
# ==========================================================

@sale_bp.route("/")
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Sale.query

    if search:

        query = query.filter(
            Sale.invoice_number.ilike(
                f"%{search}%"
            )
            | Sale.customer_name.ilike(
                f"%{search}%"
            )
            | Sale.customer_phone.ilike(
                f"%{search}%"
            )
        )

    sales = (
        query
        .order_by(
            Sale.sale_date.desc()
        )
        .all()
    )

    return render_template(
        "sales/index.html",
        sales=sales,
    )


# ==========================================================
# CREATE SALE
# ==========================================================

@sale_bp.route(
    "/create",
    methods=["GET", "POST"]
)
def create():

    if request.method == "POST":

        try:

            items = json.loads(
                request.form["cart_items"]
            )

            # ======================================================
            # PAYMENT DETAILS
            # ======================================================

            payment_method = request.form[
                "payment_method"
            ]

            amount_paid = request.form.get(
                "amount_paid",
                "0",
            ).strip()

            if amount_paid == "":
                amount_paid = "0"

            payment_currency = (
                request.form.get(
                    "payment_currency",
                    "UGX",
                )
                .strip()
                .upper()
                or "UGX"
            )

            manual_exchange_rate = request.form.get(
                "manual_exchange_rate",
                "",
            ).strip() or None

            due_date = (
                request.form.get(
                    "due_date"
                )
                or None
            )

            if due_date:

                try:

                    due_date = datetime.strptime(
                        due_date,
                        "%Y-%m-%d",
                    ).date()

                except ValueError:

                    raise Exception(
                        "Invalid due date."
                    )

            payment_reference = (
                request.form.get(
                    "payment_reference"
                )
            )

            payment_notes = (
                request.form.get(
                    "payment_notes"
                )
            )

            # ======================================================
            # CREATE SALE
            # ======================================================

            SaleService.create_sale(
                customer_id=request.form.get(
                    "customer_id"
                ),
                customer_name=request.form.get(
                    "customer_name"
                ),
                customer_phone=request.form.get(
                    "customer_phone"
                ),
                payment_method=payment_method,
                created_by=session[
                    "user_id"
                ],
                items=items,

                # Payment
                amount_paid=amount_paid,
                payment_currency=payment_currency,
                manual_exchange_rate=manual_exchange_rate,

                # Credit / installment
                due_date=due_date,
                payment_reference=payment_reference,
                payment_notes=payment_notes,
            )

            flash(
                "Sale completed successfully.",
                "success",
            )

            return redirect(
                url_for("sale.index")
            )

        except Exception as e:

            flash(
                str(e),
                "danger",
            )

    # ==========================================================
    # LOAD POS DATA
    # ==========================================================

    brands = (
        Brand.query
        .order_by(
            Brand.name
        )
        .all()
    )

    products = (
        Product.query
        .order_by(
            Product.name
        )
        .all()
    )

    variants = (
        ProductVariant.query
        .order_by(
            ProductVariant.sku
        )
        .all()
    )

    imeis = (
        IMEI.query
        .filter_by(
            status="In Stock"
        )
        .all()
    )

    settings = (
        SystemSetting.get_settings()
    )

    # ==========================================================
    # ACTIVE CURRENCIES
    # ==========================================================

    currencies = (
        Currency.query
        .filter_by(
            is_active=True
        )
        .order_by(
            Currency.code
        )
        .all()
    )

    # ==========================================================
    # PRESELECT CUSTOMER
    # ==========================================================

    selected_customer = None

    customer_id = request.args.get(
        "customer_id",
        type=int,
    )

    if customer_id:

        selected_customer = (
            Customer.query.get(
                customer_id
            )
        )

    return render_template(
        "sales/create.html",

        brands=brands,
        products=products,
        variants=variants,
        imeis=imeis,

        settings=settings,
        currencies=currencies,

        selected_customer=selected_customer,
    )


# ==========================================================
# VIEW SALE
# ==========================================================

@sale_bp.route(
    "/view/<int:sale_id>"
)
def view_sale(sale_id):

    sale = Sale.query.get_or_404(
        sale_id
    )

    currencies = (
        Currency.query
        .filter_by(is_active=True)
        .order_by(Currency.code)
        .all()
    )

    settings = SystemSetting.get_settings()

    # ----------------------------------------------------------
    # CUSTOMER OVERPAYMENT LEDGER
    # ----------------------------------------------------------
    # The credit is created atomically by SaleService.create_sale().
    # The view route is read-only and must never create accounting records.
    credit = CustomerCredit.query.filter_by(sale_id=sale.id).first()

    return render_template(
        "sales/view.html",
        sale=sale,
        currencies=currencies,
        settings=settings,
        overpayment_credit=credit,
    )

# ==========================================================
# CANCEL SALE
# ==========================================================

@sale_bp.route(
    "/<int:sale_id>/cancel",
    methods=["POST"],
)
def cancel_sale(sale_id):

    try:

        sale = SaleService.cancel_sale(sale_id)

        flash(
            f"Sale {sale.invoice_number} cancelled successfully. "
            "Inventory and IMEI records have been restored.",
            "success",
        )

    except Exception as e:

        flash(
            str(e),
            "danger",
        )

    return redirect(
        url_for(
            "sale.view_sale",
            sale_id=sale_id,
        )
    )

# ==========================================================
# PRINT SALE
# ==========================================================

@sale_bp.route(
    "/print/<int:sale_id>"
)
def print_sale(sale_id):

    sale = Sale.query.get_or_404(
        sale_id
    )

    company = Company.query.first()

    settings = (
        SystemSetting.get_settings()
    )

    if not company:

        company = Company(
            business_name="MINIFY GADGETS",
            tagline="Phones & Accessories",
            address="",
            phone="",
        )

    return render_template(
        "sales/print.html",
        sale=sale,
        company=company,
        settings=settings,
    )


# ==========================================================
# API â€” PRODUCTS BY BRAND
# ==========================================================

@sale_bp.route(
    "/api/products/<int:brand_id>"
)
def get_products(brand_id):

    products = (
        Product.query
        .filter_by(
            brand_id=brand_id,
            is_active=True,
        )
        .order_by(
            Product.name
        )
        .all()
    )

    return jsonify(
        [
            {
                "id": product.id,
                "name": product.name,
            }
            for product in products
        ]
    )


# ==========================================================
# API â€” VARIANTS BY PRODUCT
# ==========================================================

@sale_bp.route(
    "/api/variants/<int:product_id>"
)
def get_variants(product_id):

    variants = (
        ProductVariant.query
        .filter_by(
            product_id=product_id,
            is_active=True,
        )
        .order_by(
            ProductVariant.sku
        )
        .all()
    )

    return jsonify(
        [
            {
                "id": variant.id,
                "sku": variant.sku,
                "colour": variant.colour,
                "storage": variant.storage,
                "ram": variant.ram,
                "price": float(
                    variant.selling_price
                ),
                "stock": variant.quantity,
                "brand": variant.product.brand.name,
                "product": variant.product.name,
            }
            for variant in variants
        ]
    )


# ==========================================================
# API â€” BARCODE
# ==========================================================

@sale_bp.route(
    "/api/barcode/<path:barcode>"
)
def get_by_barcode(barcode):

    code = barcode.strip()

    variant = (
        ProductVariant.query
        .filter_by(
            barcode=code,
            is_active=True,
        )
        .first()
    )

    if not variant:

        return jsonify(
            {
                "found": False
            }
        ), 404

    return jsonify(
        {
            "found": True,
            "id": variant.id,
            "sku": variant.sku,
            "barcode": variant.barcode,

            "brand": variant.product.brand.name,
            "brand_id": variant.product.brand_id,

            "product": variant.product.name,
            "product_id": variant.product_id,

            "storage": variant.storage or "",
            "ram": variant.ram or "",
            "colour": variant.colour or "",

            "price": float(
                variant.selling_price
            ),

            "stock": variant.quantity,
        }
    )


# ==========================================================
# ADD PAYMENT TO EXISTING SALE
# ==========================================================

@sale_bp.route(
    "/<int:sale_id>/payment",
    methods=["POST"],
)
def add_payment(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    # ==========================================================
    # PAYMENT AMOUNT
    # ==========================================================

    try:
        original_amount = Decimal(
            request.form.get("amount", "0")
        )
    except (InvalidOperation, ValueError, TypeError):
        flash("Invalid payment amount.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    if original_amount <= 0:
        flash("Payment amount must be greater than zero.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    # ==========================================================
    # PAYMENT CURRENCY
    # ==========================================================

    payment_currency = (
        request.form.get("payment_currency", "UGX")
        .strip()
        .upper()
        or "UGX"
    )

    currency = CurrencyService.get_by_code(payment_currency)

    if not currency:
        flash(
            f"Currency {payment_currency} is not available.",
            "danger",
        )
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    # ==========================================================
    # EXCHANGE RATE / OPTIONAL OVERRIDE
    # ==========================================================

    manual_exchange_rate = request.form.get(
        "manual_exchange_rate", ""
    ).strip()

    try:
        if payment_currency == "UGX":
            exchange_rate = Decimal("1.00000000")
        elif manual_exchange_rate:
            exchange_rate = Decimal(manual_exchange_rate)
            if exchange_rate <= 0:
                raise ValueError
        else:
            conversion = CurrencyService.convert_currency(
                original_amount,
                payment_currency,
                "UGX",
            )
            exchange_rate = Decimal(
                str(conversion["rate"])
            )

        ugx_amount = original_amount * exchange_rate

    except (InvalidOperation, ValueError, TypeError):
        flash("Invalid exchange rate.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))
    except Exception as e:
        flash(
            f"Currency conversion failed: {e}",
            "danger",
        )
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    # ==========================================================
    # OUTSTANDING / OVERPAYMENT
    # ==========================================================

    balance_due = Decimal(str(sale.balance_due or 0))
    overpayment = max(ugx_amount - balance_due, Decimal("0.00"))
    applied_amount = min(ugx_amount, balance_due)

    payment = SalePayment(
        sale=sale,
        amount=ugx_amount,
        original_amount=original_amount,
        currency=currency,
        exchange_rate=exchange_rate,
        payment_method=request.form.get(
            "payment_method", "Cash"
        ),
        reference=request.form.get("reference"),
        notes=request.form.get("notes"),
        received_by=session["user_id"],
    )

    # ==========================================================
    # UPDATE SALE
    # ==========================================================

    sale.amount_paid = (
        Decimal(str(sale.amount_paid or 0))
        + ugx_amount
    )

    sale.balance_due = max(
        Decimal(str(sale.total_amount or 0))
        - sale.amount_paid,
        Decimal("0.00"),
    )

    sale.payment_status = (
        "Paid"
        if sale.balance_due <= 0
        else "Partial"
    )

    db.session.add(payment)

    # Keep customer overpayment separate from sales profit.
    if overpayment > 0:
        credit = CustomerCredit.query.filter_by(
            sale_id=sale.id
        ).first()

        if not credit:
            credit = CustomerCredit(
                customer_id=sale.customer_id,
                sale_id=sale.id,
                original_amount=overpayment,
                remaining_amount=overpayment,
                status="Outstanding",
            )
            db.session.add(credit)
        else:
            credit.remaining_amount = (
                Decimal(str(credit.remaining_amount or 0))
                + overpayment
            )
            credit.original_amount = (
                Decimal(str(credit.original_amount or 0))
                + overpayment
            )
            credit.status = "Outstanding"

    db.session.commit()

    # ==========================================================
    # SUCCESS MESSAGE
    # ==========================================================

    message = (
        f"Payment recorded: {currency.symbol or currency.code} "
        f"{original_amount:,.2f} = UGX {ugx_amount:,.2f}."
    )

    if overpayment > 0:
        message += (
            f" Overpayment/customer credit: "
            f"UGX {overpayment:,.2f}."
        )

    flash(message, "success")

    return redirect(
        url_for("sale.view_sale", sale_id=sale.id)
    )


# ==========================================================
# SETTLE CUSTOMER OVERPAYMENT
# ==========================================================

@sale_bp.route(
    "/<int:sale_id>/overpayment/refund",
    methods=["POST"],
)
def refund_overpayment(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    credit = CustomerCredit.query.filter_by(
        sale_id=sale.id
    ).first()

    if not credit or Decimal(str(credit.remaining_amount or 0)) <= 0:
        flash("There is no outstanding customer overpayment to settle.", "warning")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    try:
        refund_amount = Decimal(
            request.form.get("refund_amount", "0")
        )
    except (InvalidOperation, ValueError, TypeError):
        flash("Invalid refund amount.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    remaining = Decimal(str(credit.remaining_amount or 0))

    if refund_amount <= 0:
        flash("Refund amount must be greater than zero.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    if refund_amount > remaining:
        flash(
            f"Refund cannot exceed the outstanding customer credit of UGX {remaining:,.2f}.",
            "danger",
        )
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    transaction = CustomerCreditTransaction(
        credit=credit,
        transaction_type="REFUND",
        amount=refund_amount,
        payment_method=request.form.get("refund_method", "Cash"),
        reference=request.form.get("refund_reference"),
        notes=request.form.get("refund_notes"),
        processed_by=session["user_id"],
    )

    credit.remaining_amount = remaining - refund_amount

    if credit.remaining_amount <= 0:
        credit.remaining_amount = Decimal("0.00")
        credit.status = "Refunded"
    else:
        credit.status = "Partially Settled"

    db.session.add(transaction)
    db.session.commit()

    flash(
        f"Customer refund recorded: UGX {refund_amount:,.2f}. "
        f"Remaining customer credit: UGX {credit.remaining_amount:,.2f}.",
        "success",
    )

    return redirect(url_for("sale.view_sale", sale_id=sale.id))


# ==========================================================
# CONVERT CUSTOMER OVERPAYMENT TO BUSINESS INCOME
# ==========================================================

@sale_bp.route(
    "/<int:sale_id>/overpayment/convert-to-income",
    methods=["POST"],
)
def convert_overpayment_to_income(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    credit = CustomerCredit.query.filter_by(
        sale_id=sale.id
    ).first()

    if not credit or Decimal(str(credit.remaining_amount or 0)) <= 0:
        flash(
            "There is no outstanding customer overpayment to convert.",
            "warning",
        )
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    remaining = Decimal(str(credit.remaining_amount or 0))

    reason = (
        request.form.get("income_reason", "")
        .strip()
    )

    reference = (
        request.form.get("income_reference", "")
        .strip()
        or None
    )

    if not reason:
        flash(
            "A reason is required before customer credit can be converted to business income.",
            "danger",
        )
        return redirect(url_for("sale.view_sale", sale_id=sale.id))

    transaction = CustomerCreditTransaction(
        credit=credit,
        transaction_type="CONVERTED_TO_INCOME",
        amount=remaining,
        payment_method="Business Income",
        reference=reference,
        notes=reason,
        processed_by=session["user_id"],
    )

    credit.remaining_amount = Decimal("0.00")
    credit.status = "Converted to Income"

    db.session.add(transaction)
    db.session.commit()

    flash(
        f"UGX {remaining:,.2f} customer credit converted to business income. "
        "The original sale profit remains unchanged; this amount is recorded as additional business income.",
        "success",
    )

    return redirect(
        url_for("sale.view_sale", sale_id=sale.id)
    )


# ==========================================================
# API â€” IMEIs
# ==========================================================

@sale_bp.route(
    "/api/imeis/<int:variant_id>"
)
def get_imeis(variant_id):

    imeis = (
        IMEI.query
        .filter_by(
            product_variant_id=variant_id,
            status="In Stock",
        )
        .all()
    )

    return jsonify(
        [
            {
                "id": imei.id,
                "imei": imei.imei,
                "serial_number": imei.serial_number,
            }
            for imei in imeis
        ]
    )