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

from sqlalchemy.exc import IntegrityError

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

        # ======================================================
        # CLEAN INPUT
        # ======================================================

        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        alternative_phone = request.form.get("alternative_phone", "").strip()
        email = request.form.get("email", "").strip()
        national_id = request.form.get("national_id", "").strip()
        address = request.form.get("address", "").strip()
        business_name = request.form.get("business_name", "").strip()
        customer_type = request.form.get(
            "customer_type",
            "Retail",
        ).strip()

        # ======================================================
        # BASIC VALIDATION
        # ======================================================

        if not full_name:
            flash("Customer name is required.", "danger")
            return render_template(
                "customers/create.html",
                return_to=return_to,
            )

        if not phone:
            flash("Customer phone number is required.", "danger")
            return render_template(
                "customers/create.html",
                return_to=return_to,
            )

        # ======================================================
        # DUPLICATE PHONE CHECK
        # ======================================================

        existing_customer = Customer.query.filter_by(phone=phone).first()

        if existing_customer:

            flash(
                f"A customer with phone number {phone} already exists: "
                f"{existing_customer.full_name}.",
                "warning",
            )

            # If coming from the Sales POS, send the user back
            # with the existing customer selected.
            if return_to == "sale":
                return redirect(
                    url_for(
                        "sale.create",
                        customer_id=existing_customer.id,
                    )
                )

            # Otherwise open the existing customer's profile.
            return redirect(
                url_for(
                    "customer.view",
                    id=existing_customer.id,
                )
            )

        # ======================================================
        # CREATE CUSTOMER
        # ======================================================

        customer = Customer(
            customer_code=CustomerService.generate_customer_code(),
            full_name=full_name,
            phone=phone,
            alternative_phone=alternative_phone or None,
            email=email or None,
            national_id=national_id or None,
            address=address or None,
            business_name=business_name or None,
            customer_type=customer_type or "Retail",
        )

        try:

            db.session.add(customer)
            db.session.commit()

        except Exception:

            # Always clear the failed transaction.
            db.session.rollback()

            # A duplicate may have been created by another
            # request between our check and commit.
            existing_customer = Customer.query.filter_by(phone=phone).first()

            if existing_customer:

                flash(
                    f"A customer with phone number {phone} already exists: "
                    f"{existing_customer.full_name}.",
                    "warning",
                )

                if return_to == "sale":
                    return redirect(
                        url_for(
                            "sale.create",
                            customer_id=existing_customer.id,
                        )
                    )

                return redirect(
                    url_for(
                        "customer.view",
                        id=existing_customer.id,
                    )
                )

            flash(
                "Unable to create customer. Please check the information "
                "and try again.",
                "danger",
            )

            return render_template(
                "customers/create.html",
                return_to=return_to,
            )

        # ======================================================
        # SUCCESS
        # ======================================================

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


@customer_bp.route("/<int:id>/deactivate", methods=["POST"])
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


@customer_bp.route("/<int:id>/activate", methods=["POST"])
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
