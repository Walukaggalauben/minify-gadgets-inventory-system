from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from services.product_service import ProductService
from models.category import Category
from models.brand import Brand

from utils.permissions import permission_required

product_bp = Blueprint("product", __name__)


def login_required():
    return "user_id" in session


@product_bp.route("/products")
@permission_required("products.view")
def index():

    if not login_required():
        return redirect("/")

    search = request.args.get("search", "").strip()

    products = ProductService.get_all()

    if search:
        products = [p for p in products if search.lower() in p.name.lower()]

    return render_template(
        "products/index.html",
        products=products,
        search=search,
    )


@product_bp.route(
    "/products/create",
    methods=["GET", "POST"],
)
@permission_required("products.create")
def create():

    if not login_required():
        return redirect("/")

    categories = Category.query.filter_by(is_active=True).all()

    brands = Brand.query.filter_by(is_active=True).all()

    if request.method == "POST":

        try:

            ProductService.create(request.form)

            flash(
                "Product created successfully.",
                "success",
            )

            return redirect(url_for("product.index"))

        except Exception as e:

            flash(
                str(e),
                "danger",
            )

            print(
                "PRODUCT CREATE ERROR:",
                e,
            )

    return render_template(
        "products/create.html",
        categories=categories,
        brands=brands,
    )


@product_bp.route(
    "/products/edit/<int:id>",
    methods=["GET", "POST"],
)
@permission_required("products.edit")
def edit(id):

    if not login_required():
        return redirect("/")

    product = ProductService.get(id)

    categories = Category.query.filter_by(is_active=True).all()

    brands = Brand.query.filter_by(is_active=True).all()

    if request.method == "POST":

        ProductService.update(
            product,
            request.form,
        )

        flash(
            "Product updated successfully.",
            "success",
        )

        return redirect(url_for("product.index"))

    return render_template(
        "products/edit.html",
        product=product,
        categories=categories,
        brands=brands,
    )


@product_bp.route("/products/toggle/<int:id>")
@permission_required("products.edit")
def toggle(id):

    if not login_required():
        return redirect("/")

    product = ProductService.get(id)

    ProductService.toggle_status(product)

    flash(
        "Product status updated.",
        "success",
    )

    return redirect(url_for("product.index"))
