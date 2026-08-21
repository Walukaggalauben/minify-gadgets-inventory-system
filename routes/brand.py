from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from services.brand_service import BrandService

from utils.permissions import permission_required

brand_bp = Blueprint(
    "brand",
    __name__,
)


def login_required():
    return "user_id" in session


@brand_bp.route("/brands")
@permission_required("brands.view")
def index():

    if not login_required():
        return redirect("/")

    search = (
        request.args.get(
            "search",
            "",
        )
        .strip()
        .lower()
    )

    brands = BrandService.get_all()

    if search:
        brands = [b for b in brands if search in b.name.lower()]

    return render_template(
        "brands/index.html",
        brands=brands,
        search=search,
    )


@brand_bp.route(
    "/brands/create",
    methods=["GET", "POST"],
)
@permission_required("brands.create")
def create():

    if not login_required():
        return redirect("/")

    if request.method == "POST":

        BrandService.create(request.form)

        flash(
            "Brand created successfully.",
            "success",
        )

        return redirect(url_for("brand.index"))

    return render_template("brands/create.html")


@brand_bp.route(
    "/brands/edit/<int:id>",
    methods=["GET", "POST"],
)
@permission_required("brands.edit")
def edit(id):

    if not login_required():
        return redirect("/")

    brand = BrandService.get(id)

    if request.method == "POST":

        BrandService.update(
            brand,
            request.form,
        )

        flash(
            "Brand updated successfully.",
            "success",
        )

        return redirect(url_for("brand.index"))

    return render_template(
        "brands/edit.html",
        brand=brand,
    )


@brand_bp.route("/brands/toggle/<int:id>", methods=["POST"])
@permission_required("brands.edit")
def toggle(id):

    if not login_required():
        return redirect("/")

    brand = BrandService.get(id)

    BrandService.toggle_status(brand)

    flash(
        "Brand status updated.",
        "success",
    )

    return redirect(url_for("brand.index"))
