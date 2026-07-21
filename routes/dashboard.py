from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect

from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    stats = DashboardService.get_statistics()

    return render_template(

        "dashboard/index.html",

        stats=stats

    )