from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session

from models.product_variant import ProductVariant
from models.imei import IMEI
from services.sale_service import SaleService


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

                invoice_number=datetime.now().strftime("INV%Y%m%d%H%M%S"),

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

    variants = ProductVariant.query.order_by(
        ProductVariant.sku
    ).all()

    imeis = IMEI.query.filter_by(
        status="In Stock"
    ).all()

    return render_template(

        "sales/create.html",

        variants=variants,

        imeis=imeis

    )