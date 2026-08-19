from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from db import db

from models.trade_in_rule import TradeInRule

from utils.auth import login_required
from utils.permissions import permission_required

trade_in_rules_bp = Blueprint(
    "trade_in_rules",
    __name__,
    url_prefix="/trade-in-rules",
)


@trade_in_rules_bp.route("/", methods=["GET", "POST"])
@permission_required("settings.edit")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        ids = request.form.getlist("id[]")
        amounts = request.form.getlist("amount[]")

        for i in range(len(ids)):

            rule = TradeInRule.query.get(int(ids[i]))

            if rule:

                rule.deduction_amount = amounts[i]

        db.session.commit()

        flash(
            "Trade-In valuation rules updated successfully.",
            "success",
        )

        return redirect(url_for("trade_in_rules.index"))

    rules = TradeInRule.query.order_by(TradeInRule.rule_name).all()

    return render_template(
        "settings/trade_in_rules.html",
        rules=rules,
    )
