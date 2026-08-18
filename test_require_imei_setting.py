from decimal import Decimal

from app import create_app
from db import db

from models.system_setting import SystemSetting
from models.product_variant import ProductVariant
from models.imei import IMEI
from models.sale import Sale

from services.sale_service import SaleService


app = create_app()

with app.app_context():

    variant = db.session.get(ProductVariant, 384)
    imei = db.session.get(IMEI, 5608)
    settings = SystemSetting.get_settings()

    original_require_imei = settings.require_imei_when_available
    original_require_customer = settings.require_customer_on_sale

    original_quantity = variant.quantity
    original_imei_status = imei.status

    selling_price = Decimal(str(variant.selling_price))

    print("TEST VARIANT:", variant.id)
    print("TEST SKU:", variant.sku)
    print("TEST IMEI ID:", imei.id)
    print("TEST IMEI:", imei.imei)
    print("ORIGINAL QUANTITY:", original_quantity)
    print("ORIGINAL IMEI STATUS:", original_imei_status)
    print("ORIGINAL REQUIRE IMEI:", original_require_imei)
    print("ORIGINAL REQUIRE CUSTOMER:", original_require_customer)

    try:

        # ==================================================
        # ISOLATE IMEI SETTING
        # ==================================================

        settings.require_customer_on_sale = False
        db.session.commit()

        # ==================================================
        # TEST 1
        # REQUIRE IMEI ENABLED + NO IMEI
        # ==================================================

        settings.require_imei_when_available = True
        db.session.commit()

        print("REQUIRE IMEI ENABLED")
        print("CUSTOMER REQUIREMENT DISABLED FOR TEST ISOLATION")

        try:

            SaleService.create_sale(
                customer_id=None,
                customer_name="TEST IMEI CUSTOMER",
                customer_phone="0700000000",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "price": selling_price,
                        "price_override": False,
                    }
                ],
                amount_paid=selling_price,
                payment_currency="UGX",
            )

            print(
                "FAIL: SALE WITHOUT IMEI WAS ALLOWED "
                "WHEN REQUIRE IMEI ENABLED"
            )

        except Exception as e:

            print("EXPECTED ERROR:", str(e))

            if "select an IMEI" in str(e):

                print(
                    "PASS: SALE WITHOUT IMEI BLOCKED "
                    "WHEN REQUIRE IMEI ENABLED"
                )

            else:

                print(
                    "FAIL: WRONG ERROR WHEN IMEI REQUIRED"
                )

        db.session.rollback()

        # ==================================================
        # TEST 2
        # REQUIRE IMEI DISABLED + NO IMEI
        # ==================================================

        settings = SystemSetting.get_settings()

        settings.require_customer_on_sale = False
        settings.require_imei_when_available = False

        db.session.commit()

        variant = db.session.get(ProductVariant, 384)

        print("REQUIRE IMEI DISABLED")

        try:

            sale = SaleService.create_sale(
                customer_id=None,
                customer_name="TEST IMEI CUSTOMER",
                customer_phone="0700000000",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "price": selling_price,
                        "price_override": False,
                    }
                ],
                amount_paid=selling_price,
                payment_currency="UGX",
            )

            print("TEST SALE ID:", sale.id)

            print(
                "PASS: SALE WITHOUT IMEI ALLOWED "
                "WHEN REQUIRE IMEI DISABLED"
            )

        except Exception as e:

            print(
                "FAIL: SALE WITHOUT IMEI REJECTED "
                "WHEN REQUIRE IMEI DISABLED:",
                str(e),
            )

        db.session.rollback()

        # ==================================================
        # TEST 3
        # REQUIRE IMEI ENABLED + VALID IMEI
        # ==================================================

        settings = SystemSetting.get_settings()

        settings.require_customer_on_sale = False
        settings.require_imei_when_available = True

        db.session.commit()

        variant = db.session.get(ProductVariant, 384)
        imei = db.session.get(IMEI, 5608)

        print("REQUIRE IMEI ENABLED + VALID IMEI")

        try:

            sale = SaleService.create_sale(
                customer_id=None,
                customer_name="TEST IMEI CUSTOMER",
                customer_phone="0700000000",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "imei_id": imei.id,
                        "price": selling_price,
                        "price_override": False,
                    }
                ],
                amount_paid=selling_price,
                payment_currency="UGX",
            )

            print("TEST SALE ID:", sale.id)

            print(
                "QUANTITY DURING TEST:",
                variant.quantity
            )

            print(
                "IMEI STATUS DURING TEST:",
                imei.status
            )

            if variant.quantity == original_quantity - 2:
                print("PASS: INVENTORY REDUCED FOR TEST SALE")
            else:
                print("FAIL: INVENTORY QUANTITY INCORRECT")

            if imei.status == "Sold":
                print("PASS: IMEI MARKED SOLD")
            else:
                print("FAIL: IMEI WAS NOT MARKED SOLD")

        except Exception as e:

            print(
                "FAIL: SALE WITH VALID IMEI WAS REJECTED:",
                str(e),
            )

        # ==================================================
        # CLEANUP
        # ==================================================

        db.session.rollback()

        test_sale = (
            Sale.query
            .filter_by(customer_name="TEST IMEI CUSTOMER")
            .order_by(Sale.id.desc())
            .first()
        )

        if test_sale:

            test_sale_id = test_sale.id

            db.session.delete(test_sale)
            db.session.commit()

            print("TEST SALE REMOVED:", test_sale_id)

        variant = db.session.get(ProductVariant, 384)
        imei = db.session.get(IMEI, 5608)

        variant.quantity = original_quantity
        imei.status = original_imei_status

        db.session.commit()

        print("FINAL QUANTITY:", variant.quantity)
        print("FINAL IMEI STATUS:", imei.status)

        if variant.quantity == original_quantity:
            print("PASS: INVENTORY RESTORED")
        else:
            print("FAIL: INVENTORY NOT RESTORED")

        if imei.status == original_imei_status:
            print("PASS: IMEI RESTORED")
        else:
            print("FAIL: IMEI NOT RESTORED")

    finally:

        # ==================================================
        # RESTORE ALL SETTINGS
        # ==================================================

        db.session.rollback()

        settings = SystemSetting.get_settings()

        settings.require_imei_when_available = original_require_imei
        settings.require_customer_on_sale = original_require_customer

        db.session.commit()

        print(
            "REQUIRE IMEI RESTORED:",
            settings.require_imei_when_available
        )

        print(
            "REQUIRE CUSTOMER RESTORED:",
            settings.require_customer_on_sale
        )