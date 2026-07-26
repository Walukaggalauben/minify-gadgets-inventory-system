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
from models.sale import Sale
from models.company import Company


sale_bp = Blueprint(
    "sale",
    __name__,
    url_prefix="/sales"
)


@sale_bp.route("/")
def index():

    sales = Sale.query.order_by(
        Sale.sale_date.desc()
    ).all()

    print("=" * 50)
    print("TOTAL SALES FOUND:", len(sales))

    for sale in sales:
        print(
            sale.id,
            sale.invoice_number,
            sale.customer_name,
            sale.total_amount
        )

    print("=" * 50)

    return render_template(
        "sales/index.html",
        sales=sales
    )
    
    
@sale_bp.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        try:

            items = json.loads(request.form["cart_items"])

            SaleService.create_sale(

                customer_name=request.form["customer_name"],

                customer_phone=request.form["customer_phone"],

                payment_method=request.form["payment_method"],

                created_by=session["user_id"],

                items=items

            )

            flash(
                "Sale completed successfully.",
                "success"
            )

            return redirect(
                url_for("sale.index")
            )

        except Exception as e:

            flash(
                str(e),
                "danger"
            )

    brands = Brand.query.order_by(
        Brand.name
    ).all()

    products = Product.query.order_by(
        Product.name
    ).all()

    variants = ProductVariant.query.order_by(
        ProductVariant.sku
    ).all()

    imeis = IMEI.query.filter_by(
        status="In Stock"
    ).all()

    return render_template(

        "sales/create.html",

        brands=brands,

        products=products,

        variants=variants,

        imeis=imeis

    )

# ======================================================
# VIEW SALE
# ======================================================

@sale_bp.route("/view/<int:sale_id>")
def view_sale(sale_id):

    sale = Sale.query.get_or_404(sale_id)

    return render_template(
        "sales/view.html",
        sale=sale
    )
    
    
# ======================================================
# PRINT SALE
# ======================================================

@sale_bp.route("/print/<int:sale_id>")
def print_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    company = Company.query.first()

    if not company:
        company = Company(
            business_name="MINIFY GADGETS",
            tagline="Phones & Accessories",
            address="",
            phone=""
        )

    return render_template(
        "sales/print.html",
        sale=sale,
        company=company
    )
# ======================================================
# API ROUTES
# ======================================================

@sale_bp.route("/api/products/<int:brand_id>")
def get_products(brand_id):

    products = Product.query.filter_by(
        brand_id=brand_id,
        is_active=True
    ).order_by(Product.name).all()

    return jsonify([
        {
            "id": product.id,
            "name": product.name
        }
        for product in products
    ])


@sale_bp.route("/api/variants/<int:product_id>")
def get_variants(product_id):

    variants = ProductVariant.query.filter_by(
        product_id=product_id,
        is_active=True
    ).order_by(ProductVariant.sku).all()

    return jsonify([
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
        "product": variant.product.name
    }
    for variant in variants
])


@sale_bp.route("/api/imeis/<int:variant_id>")
def get_imeis(variant_id):

    imeis = IMEI.query.filter_by(
        product_variant_id=variant_id,
        status="In Stock"
    ).all()

    return jsonify([
        {
            "id": imei.id,
            "imei": imei.imei
        }
        for imei in imeis
    ])