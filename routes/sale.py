import json

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import jsonify

from models.product_variant import ProductVariant
from models.imei import IMEI
from services.sale_service import SaleService
from models.brand import Brand
from models.product import Product
from models.customer import Customer
from models.sale import Sale
from models.company import Company
from models.system_setting import SystemSetting
from models.sale_payment import SalePayment
from datetime import datetime
from decimal import Decimal
from db import db

sale_bp = Blueprint("sale", __name__, url_prefix="/sales")


@sale_bp.route("/")
def index():

    search = request.args.get("search", "").strip()
    query = Sale.query
    if search:
        query = query.filter(
            Sale.invoice_number.ilike(f"%{search}%")
            | Sale.customer_name.ilike(f"%{search}%")
            | Sale.customer_phone.ilike(f"%{search}%")
        )
    sales = query.order_by(Sale.sale_date.desc()).all()

    print("=" * 50)
    print("TOTAL SALES FOUND:", len(sales))

    for sale in sales:
        print(sale.id, sale.invoice_number, sale.customer_name, sale.total_amount)

    print("=" * 50)

    return render_template("sales/index.html", sales=sales)


@sale_bp.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        try:

            items = json.loads(request.form["cart_items"])

            # ==========================================================
            # PAYMENT / CREDIT DETAILS
            # ==========================================================

            payment_method = request.form["payment_method"]

            amount_paid = request.form.get("amount_paid", "0").strip()

            if amount_paid == "":
                amount_paid = "0"

            due_date = request.form.get("due_date") or None

            if due_date:
                try:
                    due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                except ValueError:
                    raise Exception("Invalid due date.")

            payment_reference = request.form.get("payment_reference")

            payment_notes = request.form.get("payment_notes")

            # ==========================================================
            # CREATE SALE
            # ==========================================================

            SaleService.create_sale(
                customer_id=request.form.get("customer_id"),
                customer_name=request.form.get("customer_name"),
                customer_phone=request.form.get("customer_phone"),
                payment_method=payment_method,
                created_by=session["user_id"],
                items=items,
                # Credit / installment
                amount_paid=amount_paid,
                due_date=due_date,
                payment_reference=payment_reference,
                payment_notes=payment_notes,
            )

            flash("Sale completed successfully.", "success")

            return redirect(url_for("sale.index"))

        except Exception as e:

            flash(str(e), "danger")

    brands = Brand.query.order_by(Brand.name).all()


    products = Product.query.order_by(Product.name).all()

    variants = ProductVariant.query.order_by(ProductVariant.sku).all()

    imeis = IMEI.query.filter_by(status="In Stock").all()

    settings = SystemSetting.get_settings()

    # ==========================================================
    # PRESELECT CUSTOMER RETURNED FROM CUSTOMER REGISTRATION
    # ==========================================================

    selected_customer = None

    customer_id = request.args.get("customer_id", type=int)

    if customer_id:
        selected_customer = Customer.query.get(customer_id)

    return render_template(
        "sales/create.html",
        brands=brands,
        products=products,
        variants=variants,
        imeis=imeis,
        settings=settings,
        selected_customer=selected_customer,
    )


# ======================================================
# VIEW SALE
# ======================================================


@sale_bp.route("/view/<int:sale_id>")
def view_sale(sale_id):

    sale = Sale.query.get_or_404(sale_id)

    return render_template("sales/view.html", sale=sale)


# ======================================================
# PRINT SALE
# ======================================================


@sale_bp.route("/print/<int:sale_id>")
def print_sale(sale_id):

    sale = Sale.query.get_or_404(sale_id)

    company = Company.query.first()

    settings = SystemSetting.get_settings()

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


# ======================================================
# API ROUTES
# ======================================================


@sale_bp.route("/api/products/<int:brand_id>")
def get_products(brand_id):

    products = (
        Product.query.filter_by(brand_id=brand_id, is_active=True)
        .order_by(Product.name)
        .all()
    )

    return jsonify([{"id": product.id, "name": product.name} for product in products])


@sale_bp.route("/api/variants/<int:product_id>")
def get_variants(product_id):

    variants = (
        ProductVariant.query.filter_by(product_id=product_id, is_active=True)
        .order_by(ProductVariant.sku)
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
                "price": float(variant.selling_price),
                "stock": variant.quantity,
                # NEW
                "brand": variant.product.brand.name,
                "product": variant.product.name,
            }
            for variant in variants
        ]
    )


@sale_bp.route("/api/barcode/<path:barcode>")
def get_by_barcode(barcode):
    code = barcode.strip()
    variant = ProductVariant.query.filter_by(barcode=code, is_active=True).first()
    if not variant:
        return jsonify({"found": False}), 404
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
            "price": float(variant.selling_price),
            "stock": variant.quantity,
        }
    )


@sale_bp.route("/<int:sale_id>/payment", methods=["POST"])
def add_payment(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    amount = Decimal(request.form.get("amount", "0"))
    if amount <= 0:
        flash("Payment amount must be greater than zero.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))
    if amount > Decimal(str(sale.balance_due or 0)):
        flash("Payment exceeds the outstanding balance.", "danger")
        return redirect(url_for("sale.view_sale", sale_id=sale.id))
    payment = SalePayment(
        sale=sale,
        amount=amount,
        payment_method=request.form.get("payment_method", "Cash"),
        reference=request.form.get("reference"),
        notes=request.form.get("notes"),
        received_by=session["user_id"],
    )
    sale.amount_paid = Decimal(str(sale.amount_paid or 0)) + amount
    sale.balance_due = Decimal(str(sale.total_amount or 0)) - sale.amount_paid
    sale.payment_status = "Paid" if sale.balance_due <= 0 else "Partial"
    db.session.add(payment)
    db.session.commit()
    flash("Customer payment recorded.", "success")
    return redirect(url_for("sale.view_sale", sale_id=sale.id))


@sale_bp.route("/api/imeis/<int:variant_id>")
def get_imeis(variant_id):

    imeis = IMEI.query.filter_by(product_variant_id=variant_id, status="In Stock").all()

    return jsonify([{"id": imei.id, "imei": imei.imei} for imei in imeis])
