from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import db
from models.company import Company

company_bp = Blueprint(
    "company",
    __name__,
    url_prefix="/company"
)


@company_bp.route("/settings", methods=["GET", "POST"])
def settings():
    company = Company.query.first()

    # Create default record if none exists
    if not company:
        company = Company(
            business_name="MINIFY GADGETS",
            tagline="Phones & Accessories",
            address="",
            phone=""
        )
        db.session.add(company)
        db.session.commit()

    if request.method == "POST":
        company.business_name = request.form.get("business_name")
        company.tagline = request.form.get("tagline")
        company.address = request.form.get("address")
        company.phone = request.form.get("phone")
        company.alternate_phone = request.form.get("alternate_phone")
        company.email = request.form.get("email")
        company.website = request.form.get("website")
        company.currency = request.form.get("currency")
        company.receipt_footer = request.form.get("receipt_footer")

        db.session.commit()

        flash("Company settings updated successfully.", "success")

        return redirect(url_for("company.settings"))

    return render_template(
        "company/settings.html",
        company=company
    )