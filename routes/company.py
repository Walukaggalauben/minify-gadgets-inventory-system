from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from db import db
from models.company import Company
from utils.permissions import permission_required

import os
import uuid

company_bp = Blueprint(
    "company",
    __name__,
    url_prefix="/company"
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@company_bp.route("/settings", methods=["GET", "POST"])
@permission_required("settings.view")
def settings():

    company = Company.query.first()

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

        from utils.permissions import has_permission
        if not has_permission("settings.edit"):
            from flask import abort
            abort(403)

        company.business_name = request.form.get("business_name")
        company.tagline = request.form.get("tagline")
        company.address = request.form.get("address")
        company.phone = request.form.get("phone")
        company.alternate_phone = request.form.get("alternate_phone")
        company.email = request.form.get("email")
        company.website = request.form.get("website")
        company.currency = request.form.get("currency")
        company.receipt_footer = request.form.get("receipt_footer")

        # -----------------------------
        # Upload Logo
        # -----------------------------
        logo = request.files.get("logo")

        if logo and logo.filename != "":

            if not allowed_file(logo.filename):
                flash(
                    "Only PNG, JPG and JPEG images are allowed.",
                    "danger"
                )
                return redirect(url_for("company.settings"))

            # Delete old logo
            if company.logo:

                old_logo = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    company.logo
                )

                if os.path.exists(old_logo):
                    os.remove(old_logo)

            ext = logo.filename.rsplit(".", 1)[1].lower()

            filename = f"{uuid.uuid4().hex}.{ext}"

            logo.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            company.logo = filename

        db.session.commit()

        flash(
            "Company settings updated successfully.",
            "success"
        )

        return redirect(url_for("company.settings"))

    return render_template(
        "company/settings.html",
        company=company
    )