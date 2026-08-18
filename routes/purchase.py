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

from datetime import datetime

from utils.auth import login_required

from models.purchase import Purchase
from models.supplier import Supplier
from models.product_variant import ProductVariant

from utils.timezone import application_date

from services.purchase_service import PurchaseService

purchase_bp = Blueprint(
    "purchase",
    __name__,
    url_prefix="/purchases",
)


# ==========================================================
# PURCHASE LIST
# ==========================================================


@purchase_bp.route("/")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = Purchase.query

    # ------------------------------------------------------
    # SEARCH
    # Purchase number, invoice number or supplier name
    # ------------------------------------------------------

    if search:

        query = query.join(Supplier, Purchase.supplier_id == Supplier.id).filter(
            db.or_(
                Purchase.purchase_number.ilike(f"%{search}%"),
                Purchase.invoice_number.ilike(f"%{search}%"),
                Supplier.name.ilike(f"%{search}%"),
            )
        )

    # ------------------------------------------------------
    # STATUS FILTER
    # ------------------------------------------------------

    if status:
        query = query.filter(Purchase.status == status)

    purchases = query.order_by(Purchase.purchase_date.desc()).all()

    return render_template(
        "purchases/index.html",
        purchases=purchases,
        search=search,
        status=status,
    )


# ==========================================================
# CREATE PURCHASE
# ==========================================================


@purchase_bp.route("/create", methods=["GET", "POST"])
def create():

    if not login_required():
        return redirect(url_for("auth.login"))

    suppliers = Supplier.query.order_by(Supplier.name).all()

    variants = ProductVariant.query.filter_by(is_active=True).all()

    if request.method == "POST":

        try:

            supplier_id = int(request.form.get("supplier_id"))

            purchase_date = datetime.strptime(
                request.form.get("purchase_date"),
                "%Y-%m-%d",
            ).date()

            invoice_number = request.form.get("invoice_number")

            payment_method = request.form.get("payment_method")

            notes = request.form.get("notes")

            variant_ids = request.form.getlist("variant_id[]")

            quantities = request.form.getlist("quantity[]")

            unit_costs = request.form.getlist("unit_cost[]")

            selling_prices = request.form.getlist("default_selling_price[]")

            imei_groups = request.form.getlist("imeis[]")

            items = []

            for (
                variant_id,
                quantity,
                unit_cost,
                selling_price,
                imei_text,
            ) in zip(
                variant_ids,
                quantities,
                unit_costs,
                selling_prices,
                imei_groups,
            ):

                if not variant_id:
                    continue

                quantity = int(quantity)

                if quantity <= 0:
                    continue

                buying_price = float(unit_cost)

                default_selling_price = float(selling_price)

                imeis = [i.strip() for i in imei_text.splitlines() if i.strip()]

                items.append(
                    {
                        "product_variant_id": int(variant_id),
                        "quantity": quantity,
                        "unit_cost": buying_price,
                        "default_selling_price": default_selling_price,
                        "imeis": imeis,
                    }
                )

            if not items:

                flash(
                    "Please add at least one purchase item.",
                    "warning",
                )

                return render_template(
                    "purchases/create.html",
                    suppliers=suppliers,
                    variants=variants,
                    today=application_date().strftime("%Y-%m-%d"),
                )

            PurchaseService.create_purchase(
                supplier_id=supplier_id,
                purchase_date=purchase_date,
                invoice_number=invoice_number,
                payment_method=payment_method,
                notes=notes,
                created_by=session["user_id"],
                items=items,
            )

            flash(
                "Purchase created successfully.",
                "success",
            )

            return redirect(url_for("purchase.index"))

        except Exception as e:

            flash(
                str(e),
                "danger",
            )

    return render_template(
        "purchases/create.html",
        suppliers=suppliers,
        variants=variants,
        today=application_date().strftime("%Y-%m-%d"),
    )


# ==========================================================
# EDIT PURCHASE
# ==========================================================


@purchase_bp.route("/edit/<int:purchase_id>", methods=["GET", "POST"])
def edit(purchase_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    purchase = Purchase.query.get_or_404(purchase_id)

    # ------------------------------------------------------
    # Cancelled purchases cannot be edited
    # ------------------------------------------------------

    if purchase.status == "Cancelled":

        flash("A cancelled purchase cannot be edited.", "warning")

        return redirect(url_for("purchase.index"))

    suppliers = Supplier.query.order_by(Supplier.name).all()

    variants = ProductVariant.query.filter_by(is_active=True).all()

    if request.method == "POST":

        try:

            supplier_id = int(request.form.get("supplier_id"))

            purchase_date = datetime.strptime(
                request.form.get("purchase_date"), "%Y-%m-%d"
            ).date()

            invoice_number = request.form.get("invoice_number")

            payment_method = request.form.get("payment_method")

            notes = request.form.get("notes")

            variant_ids = request.form.getlist("variant_id[]")

            quantities = request.form.getlist("quantity[]")

            unit_costs = request.form.getlist("unit_cost[]")

            selling_prices = request.form.getlist("default_selling_price[]")

            items = []

            for (
                variant_id,
                quantity,
                unit_cost,
                selling_price,
            ) in zip(
                variant_ids,
                quantities,
                unit_costs,
                selling_prices,
            ):

                if not variant_id:
                    continue

                quantity = int(quantity)

                if quantity <= 0:
                    continue

                items.append(
                    {
                        "product_variant_id": int(variant_id),
                        "quantity": quantity,
                        "unit_cost": float(unit_cost),
                        "default_selling_price": float(selling_price),
                    }
                )

            if not items:

                flash("Please add at least one purchase item.", "warning")

                return render_template(
                    "purchases/edit.html",
                    purchase=purchase,
                    suppliers=suppliers,
                    variants=variants,
                )

            PurchaseService.update_purchase(
                purchase=purchase,
                supplier_id=supplier_id,
                purchase_date=purchase_date,
                invoice_number=invoice_number,
                payment_method=payment_method,
                notes=notes,
                items=items,
            )

            flash("Purchase updated successfully.", "success")

            return redirect(url_for("purchase.view", purchase_id=purchase.id))

        except Exception as e:

            flash(str(e), "danger")

    return render_template(
        "purchases/edit.html",
        purchase=purchase,
        suppliers=suppliers,
        variants=variants,
    )


@purchase_bp.route("/view/<int:purchase_id>")
def view(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    return render_template("purchases/view.html", purchase=purchase)


@purchase_bp.route("/print/<int:purchase_id>")
def print_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    return render_template("purchases/print.html", purchase=purchase)


# ==========================================================
# CANCEL PURCHASE
# ==========================================================


@purchase_bp.route("/cancel/<int:purchase_id>", methods=["POST"])
def cancel(purchase_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    purchase = Purchase.query.get_or_404(purchase_id)

    try:

        PurchaseService.cancel_purchase(purchase)

        flash(f"Purchase {purchase.purchase_number} cancelled successfully.", "success")

    except Exception as e:

        flash(str(e), "danger")

    return redirect(url_for("purchase.index"))
