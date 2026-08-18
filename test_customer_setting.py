from app import create_app
from db import db
from models.system_setting import SystemSetting
from services.sale_service import SaleService


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()
    original = settings.require_customer_on_sale

    print("ORIGINAL SETTING:", original)

    try:
        settings.require_customer_on_sale = True
        db.session.commit()

        print("SETTING ENABLED:", settings.require_customer_on_sale)

        try:
            SaleService.create_sale(
                customer_id=None,
                customer_name="",
                customer_phone="",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": 999999,
                        "quantity": 1,
                    }
                ],
            )

            print("FAIL: CUSTOMER REQUIREMENT DID NOT BLOCK SALE")

        except Exception as error:

            if "customer is required" in str(error).lower():
                print("PASS: CUSTOMER REQUIREMENT WORKS")
            else:
                print("FAIL: DIFFERENT VALIDATION FIRED")
                print("ERROR:", error)

    finally:
        settings.require_customer_on_sale = original
        db.session.commit()

        print("SETTING RESTORED:", settings.require_customer_on_sale)