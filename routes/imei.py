from db import db
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from models.product_variant import ProductVariant
from models.supplier import Supplier
from utils.timezone import application_date
from services.imei_service import IMEIService
from utils.auth import login_required
from utils.permissions import permission_required


imei_bp = Blueprint(
    "imei",
    __name__,
    url_prefix="/imei"
)


#def login_required():
 #   return "user_id" in session


@imei_bp.route("/")
@permission_required("imei.view")
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
@permission_required("imei.create")
def create():

    if not login_required():
        return redirect("/")

    variants = ProductVariant.query.filter_by(is_active=True).order_by(ProductVariant.sku).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == "POST":
        try:
            IMEIService.receive_device(request.form, session["user_id"])
            flash("Device received successfully. Purchase, IMEI, serial and stock were recorded together.", "success")
            return redirect(url_for("imei.index"))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            flash("Could not receive device: " + str(e), "danger")

    return render_template(
        "imei/create.html",
        variants=variants,
        suppliers=suppliers,
        today=application_date().strftime("%Y-%m-%d"),
    )


@imei_bp.route("/edit/<int:imei_id>", methods=["GET", "POST"])
@permission_required("imei.edit")
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
@permission_required("imei.delete")
def delete(imei_id):

    if not login_required():
        return redirect("/")

    imei = IMEIService.get(imei_id)

    try:
        IMEIService.delete(imei)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("imei.index"))

    flash(
        "IMEI deleted successfully.",
        "success"
    )

    return redirect(
        url_for("imei.index")
    )