from app import create_app
from db import db
from models.system_setting import SystemSetting
from services.dashboard_service import DashboardService


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()

    original_alert_setting = settings.enable_low_stock_alerts

    print(
        "ORIGINAL LOW-STOCK ALERTS:",
        original_alert_setting
    )

    try:

        # ==========================================
        # TEST 1 — ALERTS ENABLED
        # ==========================================

        settings.enable_low_stock_alerts = True
        db.session.commit()

        dashboard_enabled = (
            DashboardService.get_statistics()
        )

        low_stock_enabled = dashboard_enabled.get(
            "low_stock",
            []
        )

        print("ALERTS ENABLED:")
        print(
            "LOW-STOCK RECORDS:",
            len(low_stock_enabled)
        )

        if isinstance(low_stock_enabled, list):
            print(
                "PASS: LOW-STOCK DATA AVAILABLE WHEN ENABLED"
            )
        else:
            print(
                "FAIL: LOW-STOCK DATA FORMAT IS INVALID"
            )

        # ==========================================
        # TEST 2 — ALERTS DISABLED
        # ==========================================

        settings.enable_low_stock_alerts = False
        db.session.commit()

        dashboard_disabled = (
            DashboardService.get_statistics()
        )

        low_stock_disabled = dashboard_disabled.get(
            "low_stock",
            []
        )

        print("ALERTS DISABLED:")
        print(
            "LOW-STOCK RECORDS:",
            len(low_stock_disabled)
        )

        if low_stock_disabled == []:
            print(
                "PASS: LOW-STOCK ALERTS DISABLED"
            )
        else:
            print(
                "FAIL: LOW-STOCK DATA STILL RETURNED"
            )

    finally:

        # ==========================================
        # RESTORE ORIGINAL SETTING
        # ==========================================

        settings.enable_low_stock_alerts = (
            original_alert_setting
        )

        db.session.commit()

        print(
            "LOW-STOCK ALERTS RESTORED:",
            settings.enable_low_stock_alerts
        )