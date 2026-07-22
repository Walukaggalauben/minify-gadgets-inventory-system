

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


sale_bp = Blueprint(
    "sale",
    __name__,
    url_prefix="/sales"
)


@sale_bp.route("/")
def index():

    return render_template(
        "sales/index.html"
    )


@sale_bp.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        try:

            SaleService.create_sale(

                customer_name=request.form["customer_name"],

                customer_phone=request.form["customer_phone"],

                payment_method=request.form["payment_method"],

                created_by=session["user_id"],

                items=[{
                    "variant_id": request.form["variant_id"],
                    "imei_id": request.form.get("imei_id"),
                    "quantity": request.form["quantity"]
                }]
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
            "id": imei.id,
            "imei": imei.imei
        }
        for imei in imeis
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
            "stock": variant.quantity
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