from app import create_app
from db import db
from models.system_setting import SystemSetting


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()
    original_setting = settings.show_cashier_on_receipt

    print(
        "ORIGINAL SHOW CASHIER:",
        original_setting
    )

    try:

        with app.test_client() as client:

            # ==========================================
            # LOGIN
            # ==========================================

            login = client.post(
                "/",
                data={
                    "username": "admin",
                    "password": "admin123",
                },
                follow_redirects=False,
            )

            print(
                "LOGIN STATUS:",
                login.status_code
            )

            print(
                "LOGIN LOCATION:",
                login.headers.get("Location")
            )

            if login.status_code != 302:
                print(
                    "FAIL: TEST CLIENT COULD NOT LOGIN"
                )
                raise SystemExit(1)

            # ==========================================
            # TEST ENABLED
            # ==========================================

            settings.show_cashier_on_receipt = True
            db.session.commit()

            response = client.get(
                "/sales/print/24",
                follow_redirects=False,
            )

            html_enabled = response.get_data(
                as_text=True
            )

            print(
                "ENABLED RESPONSE STATUS:",
                response.status_code
            )

            if response.status_code != 200:
                print(
                    "FAIL: RECEIPT DID NOT RENDER"
                )
                print(
                    "LOCATION:",
                    response.headers.get("Location")
                )

            elif "Served By:" in html_enabled:
                print(
                    "PASS: CASHIER SHOWN WHEN ENABLED"
                )

            else:
                print(
                    "FAIL: CASHIER NOT SHOWN WHEN ENABLED"
                )

            # ==========================================
            # TEST DISABLED
            # ==========================================

            settings.show_cashier_on_receipt = False
            db.session.commit()

            response = client.get(
                "/sales/print/24",
                follow_redirects=False,
            )

            html_disabled = response.get_data(
                as_text=True
            )

            print(
                "DISABLED RESPONSE STATUS:",
                response.status_code
            )

            if response.status_code != 200:
                print(
                    "FAIL: RECEIPT DID NOT RENDER"
                )

            elif "Served By:" not in html_disabled:
                print(
                    "PASS: CASHIER HIDDEN WHEN DISABLED"
                )

            else:
                print(
                    "FAIL: CASHIER STILL SHOWN WHEN DISABLED"
                )

    finally:

        # ==========================================
        # RESTORE ORIGINAL SETTING
        # ==========================================

        settings.show_cashier_on_receipt = (
            original_setting
        )

        db.session.commit()

        print(
            "SHOW CASHIER RESTORED:",
            settings.show_cashier_on_receipt
        )