from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from services.supplier_service import SupplierService
from utils.auth import login_required
from utils.permissions import permission_required

supplier_bp = Blueprint(
    "supplier",
    __name__,
    url_prefix="/suppliers",
)


# ==========================================================
# SUPPLIER LIST
# ==========================================================


@supplier_bp.route("/")
@permission_required("suppliers.view")
def index():

    if not login_required():
        return redirect("/")

    search = request.args.get(
        "search",
        "",
    ).strip()

    if search:
        suppliers = SupplierService.search(search)
    else:
        suppliers = SupplierService.get_all()

    return render_template(
        "supplier/index.html",
        suppliers=suppliers,
        search=search,
    )


# ==========================================================
# CREATE SUPPLIER
# ==========================================================


@supplier_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@permission_required("suppliers.create")
def create():

    if not login_required():
        return redirect("/")

    if request.method == "POST":

        try:

            SupplierService.create(request.form)

            flash(
                "Supplier created successfully.",
                "success",
            )

            return redirect(url_for("supplier.index"))

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

    return render_template("supplier/create.html")


# ==========================================================
# EDIT SUPPLIER
# ==========================================================


@supplier_bp.route(
    "/edit/<int:supplier_id>",
    methods=["GET", "POST"],
)
@permission_required("suppliers.edit")
def edit(supplier_id):

    if not login_required():
        return redirect("/")

    supplier = SupplierService.get(supplier_id)

    if request.method == "POST":

        try:

            SupplierService.update(
                supplier,
                request.form,
            )

            flash(
                "Supplier updated successfully.",
                "success",
            )

            return redirect(url_for("supplier.index"))

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

    return render_template(
        "supplier/edit.html",
        supplier=supplier,
    )


# ==========================================================
# DELETE SUPPLIER
# ==========================================================


@supplier_bp.route(
    "/delete/<int:supplier_id>",
    methods=["POST"],
)
@permission_required("suppliers.delete")
def delete(supplier_id):

    if not login_required():
        return redirect("/")

    supplier = SupplierService.get(supplier_id)

    SupplierService.delete(supplier)

    flash(
        "Supplier deleted successfully.",
        "success",
    )

    return redirect(url_for("supplier.index"))
