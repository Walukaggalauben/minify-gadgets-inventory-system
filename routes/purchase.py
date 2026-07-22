from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from utils.auth import login_required

from models.purchase import Purchase
from models.supplier import Supplier
from models.product_variant import ProductVariant

from services.purchase_service import PurchaseService
from datetime import datetime


purchase_bp = Blueprint(
    "purchase",
    __name__,
    url_prefix="/purchases"
)

@purchase_bp.route("/")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

    purchases = (
        Purchase.query
        .order_by(Purchase.purchase_date.desc())
        .all()
    )

    return render_template(
        "purchases/index.html",
        purchases=purchases
    )
    
    
@purchase_bp.route("/create", methods=["GET", "POST"])
def create():

    if not login_required():
        return redirect(url_for("auth.login"))

    suppliers = Supplier.query.order_by(
        Supplier.name
    ).all()

    variants = (
        ProductVariant.query
        .filter_by(is_active=True)
        .all()
    )

    if request.method == "POST":

        supplier_id = request.form.get("supplier_id")

        purchase_date = datetime.strptime(
            request.form.get("purchase_date"),
            "%Y-%m-%d"
        ).date()

        invoice_number = request.form.get("invoice_number")
        payment_method = request.form.get("payment_method")
        notes = request.form.get("notes")

        # Dynamic purchase items
        variant_ids = request.form.getlist("variant_id[]")
        quantities = request.form.getlist("quantity[]")
        unit_costs = request.form.getlist("unit_cost[]")

        items = []

        for variant_id, quantity, unit_cost in zip(
            variant_ids,
            quantities,
            unit_costs
        ):

            if (
                not variant_id or
                not quantity or
                not unit_cost
            ):
                continue

            quantity = int(quantity)
            unit_cost = float(unit_cost)

            if quantity <= 0:
                continue

            if unit_cost < 0:
                continue

            items.append({
                "product_variant_id": int(variant_id),
                "quantity": quantity,
                "unit_cost": unit_cost
            })

        if not items:

            flash(
                "Please add at least one purchase item.",
                "warning"
            )

            return render_template(
                "purchases/create.html",
                suppliers=suppliers,
                variants=variants,
                today=datetime.today().strftime("%Y-%m-%d")
            )

        try:

            PurchaseService.create_purchase(
                supplier_id=int(supplier_id),
                purchase_date=purchase_date,
                invoice_number=invoice_number,
                payment_method=payment_method,
                notes=notes,
                created_by=session["user_id"],
                items=items
            )

            flash(
                "Purchase created successfully.",
                "success"
            )

            return redirect(
                url_for("purchase.index")
            )

        except Exception as e:

            flash(
                str(e),
                "danger"
            )

    return render_template(
        "purchases/create.html",
        suppliers=suppliers,
        variants=variants,
        today=datetime.today().strftime("%Y-%m-%d")
    )