from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.expense import Expense
from utils.timezone import application_now, application_date

from db import db
from utils.permissions import permission_required

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


def _number():
    return f"EXP-{application_now().strftime('%Y%m%d%H%M%S%f')[:-3]}"


@expenses_bp.route("/")
@permission_required("expenses.view")
def index():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    query = Expense.query
    if search:
        query = query.filter(
            (Expense.expense_number.ilike(f"%{search}%"))
            | (Expense.description.ilike(f"%{search}%"))
            | (Expense.reference.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(Expense.category == category)
    expenses = query.order_by(Expense.expense_date.desc(), Expense.id.desc()).all()
    total = sum((Decimal(str(x.amount or 0)) for x in expenses), Decimal("0"))
    categories = [
        x[0]
        for x in db.session.query(Expense.category)
        .distinct()
        .order_by(Expense.category)
        .all()
    ]
    return render_template(
        "expenses/index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        search=search,
        selected_category=category,
    )


@expenses_bp.route("/create", methods=["GET", "POST"])
@permission_required("expenses.create")
def create():
    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount", "0"))
            if amount <= 0:
                raise ValueError("Expense amount must be greater than zero.")
            expense = Expense(
                expense_number=_number(),
                expense_date=datetime.strptime(
                    request.form["expense_date"], "%Y-%m-%d"
                ).date(),
                category=request.form["category"].strip(),
                description=request.form["description"].strip(),
                amount=amount,
                payment_method=request.form.get("payment_method", "Cash"),
                reference=request.form.get("reference"),
                notes=request.form.get("notes"),
                created_by=session["user_id"],
            )
            if not expense.category or not expense.description:
                raise ValueError("Category and description are required.")
            db.session.add(expense)
            db.session.commit()
            flash("Expense recorded successfully.", "success")
            return redirect(url_for("expenses.index"))
        except (ValueError, InvalidOperation) as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template(
        "expenses/create.html", today=application_date().strftime("%Y-%m-%d")
    )


@expenses_bp.route("/delete/<int:id>", methods=["POST"])
@permission_required("expenses.delete")
def delete(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.index"))


# ==========================================================
# EDIT EXPENSE
# ==========================================================


@expenses_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@permission_required("expenses.edit")
def edit(id):

    expense = Expense.query.get_or_404(id)

    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount", "0"))

            if amount <= 0:
                raise ValueError("Expense amount must be greater than zero.")

            category = request.form.get("category", "").strip()

            description = request.form.get("description", "").strip()

            if not category or not description:
                raise ValueError("Category and description are required.")

            expense.expense_date = datetime.strptime(
                request.form["expense_date"],
                "%Y-%m-%d",
            ).date()

            expense.category = category
            expense.description = description
            expense.amount = amount
            expense.payment_method = request.form.get("payment_method", "Cash")
            expense.reference = request.form.get("reference")
            expense.notes = request.form.get("notes")

            db.session.commit()

            flash(
                "Expense updated successfully.",
                "success",
            )

            return redirect(url_for("expenses.index"))

        except (ValueError, InvalidOperation) as exc:
            db.session.rollback()

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "expenses/edit.html",
        expense=expense,
    )
