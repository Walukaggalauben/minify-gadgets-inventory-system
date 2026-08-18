from app import create_app
from db import db
from models.system_setting import SystemSetting
from models.sale import Sale


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()
    original_setting = settings.show_imei_on_receipt

    sale = db.session.get(Sale, 24)

    print(
        "TEST SALE:",
        sale.id
    )

    # Find actual IMEI values belonging to this sale
    imei_values = []

    for item in sale.items:

        if item.imei and item.imei.imei:
            imei_values.append(
                str(item.imei.imei)
            )

    print(
        "SALE IMEI COUNT:",
        len(imei_values)
    )

    if imei_values:
        print(
            "TEST IMEI:",
            imei_values[0]
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
            # ENABLED
            # ==========================================

            settings.show_imei_on_receipt = True
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

            elif not imei_values:

                print(
                    "PASS: RECEIPT RENDERED, BUT SALE HAS NO IMEI"
                )

            elif imei_values[0] in html_enabled:

                print(
                    "PASS: ACTUAL IMEI SHOWN WHEN ENABLED"
                )

            else:

                print(
                    "FAIL: ACTUAL IMEI NOT SHOWN WHEN ENABLED"
                )

            # ==========================================
            # DISABLED
            # ==========================================

            settings.show_imei_on_receipt = False
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

            elif not imei_values:

                print(
                    "PASS: SALE HAS NO IMEI TO DISPLAY"
                )

            elif imei_values[0] not in html_disabled:

                print(
                    "PASS: ACTUAL IMEI HIDDEN WHEN DISABLED"
                )

            else:

                print(
                    "FAIL: ACTUAL IMEI STILL RENDERED WHEN DISABLED"
                )

    finally:

        settings.show_imei_on_receipt = (
            original_setting
        )

        db.session.commit()

        print(
            "SHOW IMEI RESTORED:",
            settings.show_imei_on_receipt
        )