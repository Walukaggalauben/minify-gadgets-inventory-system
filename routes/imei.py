from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
   # session
)

from models.product_variant import ProductVariant
from services.imei_service import IMEIService
from utils.auth import login_required


imei_bp = Blueprint(
    "imei",
    __name__,
    url_prefix="/imei"
)


#def login_required():
 #   return "user_id" in session


@imei_bp.route("/")
def index():

    if not login_required():
        return redirect("/")

    search = request.args.get("search", "").strip()

    if search:
        imeis = IMEIService.search(search)
    else:
        imeis = IMEIService.get_all()

    return render_template(
        "imei/index.html",
        imeis=imeis,
        search=search
    )


@imei_bp.route("/create", methods=["GET", "POST"])
def create():

    if not login_required():
        return redirect("/")

    variants = ProductVariant.query.order_by(
        ProductVariant.sku
    ).all()

    print("Variants found:", len(variants))
    print(variants)

    if request.method == "POST":

        try:
            IMEIService.create(request.form)

            flash(
                "IMEI added successfully.",
                "success"
            )

            return redirect(
                url_for("imei.index")
            )

        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "imei/create.html",
        variants=variants
    )


@imei_bp.route("/edit/<int:imei_id>", methods=["GET", "POST"])
def edit(imei_id):

    if not login_required():
        return redirect("/")

    imei = IMEIService.get(imei_id)

    variants = ProductVariant.query.order_by(
        ProductVariant.sku
    ).all()

    if request.method == "POST":

        try:

            IMEIService.update(
                imei,
                request.form
            )

            flash(
                "IMEI updated successfully.",
                "success"
            )

            return redirect(
                url_for("imei.index")
            )

        except ValueError as e:

            flash(str(e), "danger")

    return render_template(
        "imei/edit.html",
        imei=imei,
        variants=variants
    )


@imei_bp.route("/delete/<int:imei_id>", methods=["POST"])
def delete(imei_id):

    if not login_required():
        return redirect("/")

    imei = IMEIService.get(imei_id)

    IMEIService.delete(imei)

    flash(
        "IMEI deleted successfully.",
        "success"
    )

    return redirect(
        url_for("imei.index")
    )