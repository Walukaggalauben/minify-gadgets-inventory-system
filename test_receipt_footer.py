from app import create_app
from db import db
from models.system_setting import SystemSetting


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()

    original_footer = settings.receipt_footer

    test_footer = "MINIFY GADGETS RECEIPT FOOTER TEST 84721"

    print(
        "ORIGINAL FOOTER:",
        original_footer
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

            # ==========================================
            # SET TEST FOOTER
            # ==========================================

            settings.receipt_footer = test_footer
            db.session.commit()

            response = client.get(
                "/sales/print/24",
                follow_redirects=False,
            )

            html = response.get_data(
                as_text=True
            )

            print(
                "RESPONSE STATUS:",
                response.status_code
            )

            if (
                response.status_code == 200
                and test_footer in html
            ):

                print(
                    "PASS: RECEIPT FOOTER RENDERED"
                )

            else:

                print(
                    "FAIL: RECEIPT FOOTER NOT RENDERED"
                )

    finally:

        # ==========================================
        # RESTORE ORIGINAL FOOTER
        # ==========================================

        settings.receipt_footer = original_footer

        db.session.commit()

        print(
            "RECEIPT FOOTER RESTORED:",
            settings.receipt_footer
        )