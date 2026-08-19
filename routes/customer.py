from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)

from db import db

from models.customer import Customer
from models.sale import Sale

from services.customer_service import CustomerService

from utils.auth import login_required
from utils.permissions import permission_required

customer_bp = Blueprint(
    "customer",
    __name__,
    url_prefix="/customers",
)


# ==========================================================
# CUSTOMER LIST
# ==========================================================


@customer_bp.route("/")
@permission_required("customers.view")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

    search = request.args.get(
        "search",
        "",
    ).strip()

    query = Customer.query

    if search:

        query = query.filter(
            Customer.full_name.ilike(f"%{search}%")
            | Customer.phone.ilike(f"%{search}%")
            | Customer.customer_code.ilike(f"%{search}%")
        )

    customers = query.order_by(Customer.full_name).all()

    return render_template(
        "customers/index.html",
        customers=customers,
        search=search,
    )


# ==========================================================
# CREATE CUSTOMER
# ==========================================================


@customer_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@permission_required("customers.create")
def create():

    if not login_required():
        return redirect(url_for("auth.login"))

    # Where should we return after creating the customer?
    return_to = request.args.get("return_to") or request.form.get("return_to")

    if request.method == "POST":

        customer = Customer(
            customer_code=CustomerService.generate_customer_code(),
            full_name=request.form["full_name"],
            phone=request.form["phone"],
            alternative_phone=request.form.get("alternative_phone"),
            email=request.form.get("email"),
            national_id=request.form.get("national_id"),
            address=request.form.get("address"),
            business_name=request.form.get("business_name"),
            customer_type=request.form.get(
                "customer_type",
                "Retail",
            ),
        )

        db.session.add(customer)
        db.session.commit()

        flash(
            "Customer added successfully.",
            "success",
        )

        # ======================================================
        # RETURN TO SALES POS WITH NEW CUSTOMER
        # ======================================================

        if return_to == "sale":

            return redirect(
                url_for(
                    "sale.create",
                    customer_id=customer.id,
                )
            )

        # Normal customer creation
        return redirect(url_for("customer.index"))

    return render_template(
        "customers/create.html",
        return_to=return_to,
    )


# ==========================================================
# CUSTOMER PROFILE
# ==========================================================


@customer_bp.route("/<int:id>")
@permission_required("customers.view")
def view(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    customer = Customer.query.get_or_404(id)

    purchase_count = Sale.query.filter(
        Sale.customer_id == customer.id,
        Sale.status != "Cancelled",
    ).count()

    outstanding_balance = (
        db.session.query(
            db.func.coalesce(
                db.func.sum(Sale.balance_due),
                0,
            )
        )
        .filter(
            Sale.customer_id == customer.id,
            Sale.status != "Cancelled",
            Sale.balance_due > 0,
        )
        .scalar()
    )

    lifetime_spend = (
        db.session.query(
            db.func.coalesce(
                db.func.sum(Sale.total_amount),
                0,
            )
        )
        .filter(
            Sale.customer_id == customer.id,
            Sale.status != "Cancelled",
        )
        .scalar()
    )

    recent_sales = (
        Sale.query.filter_by(customer_id=customer.id)
        .order_by(Sale.sale_date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "customers/view.html",
        customer=customer,
        purchase_count=purchase_count,
        lifetime_spend=lifetime_spend,
        outstanding_balance=outstanding_balance,
        recent_sales=recent_sales,
    )


# ==========================================================
# EDIT CUSTOMER
# ==========================================================


@customer_bp.route(
    "/<int:id>/edit",
    methods=["GET", "POST"],
)
@permission_required("customers.edit")
def edit(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    customer = Customer.query.get_or_404(id)

    if request.method == "POST":

        customer.full_name = request.form["full_name"]

        customer.phone = request.form["phone"]

        customer.alternative_phone = request.form.get("alternative_phone")

        customer.email = request.form.get("email")

        customer.national_id = request.form.get("national_id")

        customer.address = request.form.get("address")

        customer.business_name = request.form.get("business_name")

        customer.customer_type = request.form.get("customer_type")

        db.session.commit()

        flash(
            "Customer updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "customer.view",
                id=customer.id,
            )
        )

    return render_template(
        "customers/edit.html",
        customer=customer,
    )


# ==========================================================
# DEACTIVATE CUSTOMER
# ==========================================================


@customer_bp.route("/<int:id>/deactivate")
@permission_required("customers.edit")
def deactivate(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    customer = Customer.query.get_or_404(id)

    customer.is_active = False

    db.session.commit()

    flash(
        "Customer deactivated successfully.",
        "success",
    )

    return redirect(url_for("customer.index"))


# ==========================================================
# REACTIVATE CUSTOMER
# ==========================================================


@customer_bp.route("/<int:id>/activate")
@permission_required("customers.edit")
def activate(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    customer = Customer.query.get_or_404(id)

    customer.is_active = True

    db.session.commit()

    flash(
        "Customer activated successfully.",
        "success",
    )

    return redirect(url_for("customer.index"))


# ==========================================================
# CUSTOMER SEARCH API
# ==========================================================


@customer_bp.route("/api/search")
@permission_required("customers.view")
def search():

    if not login_required():
        return jsonify([])

    q = request.args.get(
        "q",
        "",
    ).strip()

    if not q:
        return jsonify([])

    customers = (
        Customer.query.filter(
            Customer.is_active == True,
            (
                Customer.full_name.ilike(f"%{q}%")
                | Customer.phone.ilike(f"%{q}%")
                | Customer.customer_code.ilike(f"%{q}%")
            ),
        )
        .limit(10)
        .all()
    )

    return jsonify(
        [
            {
                "id": c.id,
                "code": c.customer_code,
                "name": c.full_name,
                "phone": c.phone,
                "alternative_phone": c.alternative_phone,
                "business_name": c.business_name,
                "email": c.email,
                "national_id": c.national_id,
                "address": c.address,
            }
            for c in customers
        ]
    )
