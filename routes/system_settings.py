from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from db import db
from models.system_setting import SystemSetting
from services.currency_service import CurrencyService

system_settings_bp = Blueprint(
    "system_settings",
    __name__,
    url_prefix="/system-settings",
)


@system_settings_bp.route("/", methods=["GET", "POST"])
def index():

    settings = SystemSetting.get_settings()

    currencies = CurrencyService.get_active_currencies()

    if request.method == "POST":

        try:

            # ==========================================
            # GENERAL SETTINGS
            # ==========================================

            currency_code = request.form.get("currency", "UGX").strip().upper()

            selected_currency = CurrencyService.get_by_code(currency_code)

            if selected_currency is None:

                flash("Invalid currency selected.", "danger")

                return redirect(url_for("system_settings.index"))

            settings.currency = selected_currency.code

            settings.timezone = (
                request.form.get("timezone", "Africa/Kampala").strip()
                or "Africa/Kampala"
            )

            settings.date_format = (
                request.form.get("date_format", "DD/MM/YYYY").strip() or "DD/MM/YYYY"
            )

            # ==========================================
            # INVENTORY SETTINGS
            # ==========================================

            minimum_stock = request.form.get("default_minimum_stock", type=int)

            settings.default_minimum_stock = max(
                minimum_stock if minimum_stock is not None else 1, 0
            )

            settings.enable_low_stock_alerts = "enable_low_stock_alerts" in request.form

            settings.prevent_negative_stock = "prevent_negative_stock" in request.form

            # ==========================================
            # SALES SETTINGS
            # ==========================================

            settings.require_customer_on_sale = (
                "require_customer_on_sale" in request.form
            )

            settings.require_imei_when_available = (
                "require_imei_when_available" in request.form
            )

            settings.allow_price_override = "allow_price_override" in request.form

            # ==========================================
            # RECEIPT SETTINGS
            # ==========================================

            receipt_footer = request.form.get("receipt_footer", "").strip()

            settings.receipt_footer = (
                receipt_footer or "Thank you for shopping with us."
            )

            settings.show_imei_on_receipt = "show_imei_on_receipt" in request.form

            settings.show_cashier_on_receipt = "show_cashier_on_receipt" in request.form

            # ==========================================
            # PURCHASING SETTINGS
            # ==========================================

            settings.auto_update_buying_price = (
                "auto_update_buying_price" in request.form
            )

            # ==========================================
            # SYSTEM SETTINGS
            # ==========================================

            records_per_page = request.form.get("records_per_page", type=int)

            if records_per_page not in (
                10,
                25,
                50,
                100,
            ):
                records_per_page = 25

            settings.records_per_page = records_per_page

            session_timeout = request.form.get("session_timeout_minutes", type=int)

            settings.session_timeout_minutes = max(
                session_timeout if session_timeout is not None else 60, 5
            )

            # ==========================================
            # SAVE
            # ==========================================

            db.session.commit()

            flash("System settings updated successfully.", "success")

            return redirect(url_for("system_settings.index"))

        except Exception as error:

            db.session.rollback()

            print("SYSTEM SETTINGS ERROR:", error)

            flash("Unable to save system settings. " "Please try again.", "danger")

    return render_template(
        "settings/index.html",
        settings=settings,
        currencies=currencies,
    )

@system_settings_bp.route(
    "/currency-rate",
    methods=["GET"]
)
def currency_rate():

    from_currency = (
        request.args.get(
            "from",
            ""
        )
        .strip()
        .upper()
    )

    to_currency = (
        request.args.get(
            "to",
            ""
        )
        .strip()
        .upper()
    )

    if not from_currency or not to_currency:

        return {
            "success": False,
            "message": (
                "Both source and target currencies "
                "are required."
            ),
        }, 400

    try:

        rate = CurrencyService.get_rate(
            from_currency,
            to_currency,
        )

        return {
            "success": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": float(rate),
        }

    except Exception as error:

        print(
            "CURRENCY RATE ERROR:",
            error
        )

        return {
            "success": False,
            "message": str(error),
        }, 400
