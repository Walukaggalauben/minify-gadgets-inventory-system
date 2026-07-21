from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from services.product_variant_service import ProductVariantService
from models.product import Product

variant_bp = Blueprint("variant", __name__)


def login_required():
    return "user_id" in session


@variant_bp.route("/variants")
def index():

    if not login_required():
        return redirect("/")

    search = request.args.get("search", "").strip().lower()

    variants = ProductVariantService.get_all()

    if search:

        variants = [
            v for v in variants
            if (
                search in v.product.name.lower()
                or search in (v.sku or "").lower()
                or search in (v.barcode or "").lower()
                or search in (v.storage or "").lower()
                or search in (v.ram or "").lower()
                or search in (v.colour or "").lower()
            )
        ]

    return render_template(
        "product_variants/index.html",
        variants=variants,
        search=search
    )


@variant_bp.route("/variants/create", methods=["GET", "POST"])
def create():

    if not login_required():
        return redirect("/")

    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()

    if request.method == "POST":

        ProductVariantService.create(request.form)

        flash(
            "Product Variant created successfully.",
            "success"
        )

        return redirect(url_for("variant.index"))

    return render_template(
        "product_variants/create.html",
        products=products
    )


@variant_bp.route("/variants/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if not login_required():
        return redirect("/")

    variant = ProductVariantService.get(id)

    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()

    if request.method == "POST":

        ProductVariantService.update(
            variant,
            request.form
        )

        flash(
            "Product Variant updated successfully.",
            "success"
        )

        return redirect(url_for("variant.index"))

    return render_template(
        "product_variants/edit.html",
        variant=variant,
        products=products
    )


@variant_bp.route("/variants/toggle/<int:id>")
def toggle(id):

    if not login_required():
        return redirect("/")

    variant = ProductVariantService.get(id)

    ProductVariantService.toggle_status(variant)

    flash(
        "Product Variant status updated.",
        "success"
    )

    return redirect(url_for("variant.index"))