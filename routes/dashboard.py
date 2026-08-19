from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import jsonify
from utils.permissions import permission_required

from sqlalchemy import func

from db import db

from models.sale import Sale
from models.system_setting import SystemSetting

from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)


# ==========================================================
# DASHBOARD
# ==========================================================


@dashboard_bp.route("/dashboard")
@permission_required("dashboard.view")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    stats = DashboardService.get_statistics()

    settings = SystemSetting.get_settings()

    return render_template("dashboard/index.html", stats=stats, settings=settings)


# ==========================================================
# MONTHLY SALES CHART
# ==========================================================


@dashboard_bp.route("/monthly-sales-data")
@permission_required("dashboard.view")
def monthly_sales_data():

    results = (
        db.session.query(
            func.extract("month", Sale.sale_date).label("month"),
            func.sum(Sale.total_amount).label("sales"),
        )
        .group_by(func.extract("month", Sale.sale_date))
        .order_by(func.extract("month", Sale.sale_date))
        .all()
    )

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    labels = []
    values = []

    for row in results:

        labels.append(months[int(row.month) - 1])

        values.append(float(row.sales or 0))

    return jsonify(
        {
            "labels": labels,
            "values": values,
        }
    )
