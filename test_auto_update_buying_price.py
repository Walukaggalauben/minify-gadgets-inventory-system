from decimal import Decimal
from datetime import datetime

from app import create_app
from db import db
from models.product_variant import ProductVariant
from models.system_setting import SystemSetting
from services.purchase_service import PurchaseService


app = create_app()

with app.app_context():

    variant = db.session.get(
        ProductVariant,
        384
    )

    settings = SystemSetting.get_settings()

    original_setting = (
        settings.auto_update_buying_price
    )

    original_buying = Decimal(
        str(variant.buying_price)
    )

    original_selling = Decimal(
        str(variant.selling_price)
    )

    original_quantity = variant.quantity

    print(
        "TEST VARIANT:",
        variant.id
    )

    print(
        "TEST SKU:",
        variant.sku
    )

    print(
        "ORIGINAL BUYING PRICE:",
        original_buying
    )

    print(
        "ORIGINAL SELLING PRICE:",
        original_selling
    )

    print(
        "ORIGINAL QUANTITY:",
        original_quantity
    )

    print(
        "ORIGINAL AUTO-UPDATE:",
        original_setting
    )

    try:

        # ==================================================
        # TEST DISABLED
        # ==================================================

        settings.auto_update_buying_price = False
        db.session.commit()

        print(
            "AUTO-UPDATE DISABLED"
        )

        test_buying = (
            original_buying + Decimal("1000")
        )

        test_selling = (
            original_selling + Decimal("2000")
        )

        try:

            PurchaseService.create_purchase(
                supplier_id=1,
                purchase_date=datetime.utcnow(),
                invoice_number="TEST-AUTO-UPDATE-DISABLED",
                payment_method="Cash",
                notes="AUTOMATED SETTING TEST",
                created_by=1,
                items=[
                    {
                        "product_variant_id": variant.id,
                        "quantity": 1,
                        "unit_cost": test_buying,
                        "default_selling_price": test_selling,
                        "imeis": [],
                    }
                ],
            )

            db.session.refresh(variant)

            print(
                "BUYING AFTER DISABLED:",
                variant.buying_price
            )

            print(
                "SELLING AFTER DISABLED:",
                variant.selling_price
            )

            if (
                Decimal(str(variant.buying_price))
                == original_buying
                and
                Decimal(str(variant.selling_price))
                == original_selling
            ):

                print(
                    "PASS: PRICES UNCHANGED WHEN DISABLED"
                )

            else:

                print(
                    "FAIL: PRICES CHANGED WHEN DISABLED"
                )

        except Exception as e:

            print(
                "UNEXPECTED ERROR DISABLED:",
                str(e)
            )

        # Roll back the test purchase
        db.session.rollback()

        variant = db.session.get(
            ProductVariant,
            384
        )

        # ==================================================
        # TEST ENABLED
        # ==================================================

        settings = SystemSetting.get_settings()

        settings.auto_update_buying_price = True
        db.session.commit()

        print(
            "AUTO-UPDATE ENABLED"
        )

        test_buying = (
            original_buying + Decimal("1000")
        )

        test_selling = (
            original_selling + Decimal("2000")
        )

        try:

            PurchaseService.create_purchase(
                supplier_id=1,
                purchase_date=datetime.utcnow(),
                invoice_number="TEST-AUTO-UPDATE-ENABLED",
                payment_method="Cash",
                notes="AUTOMATED SETTING TEST",
                created_by=1,
                items=[
                    {
                        "product_variant_id": variant.id,
                        "quantity": 1,
                        "unit_cost": test_buying,
                        "default_selling_price": test_selling,
                        "imeis": [],
                    }
                ],
            )

            db.session.refresh(variant)

            print(
                "BUYING AFTER ENABLED:",
                variant.buying_price
            )

            print(
                "SELLING AFTER ENABLED:",
                variant.selling_price
            )

            if (
                Decimal(str(variant.buying_price))
                == test_buying
                and
                Decimal(str(variant.selling_price))
                == test_selling
            ):

                print(
                    "PASS: PRICES UPDATED WHEN ENABLED"
                )

            else:

                print(
                    "FAIL: PRICES NOT UPDATED WHEN ENABLED"
                )

        except Exception as e:

            print(
                "UNEXPECTED ERROR ENABLED:",
                str(e)
            )

        # Roll back the test purchase and price changes
        db.session.rollback()

        # ==================================================
        # VERIFY INVENTORY RESTORED
        # ==================================================

        variant = db.session.get(
            ProductVariant,
            384
        )

        print(
            "QUANTITY AFTER ROLLBACK:",
            variant.quantity
        )

        if variant.quantity == original_quantity:

            print(
                "PASS: INVENTORY QUANTITY RESTORED"
            )

        else:

            print(
                "FAIL: INVENTORY QUANTITY CHANGED"
            )

        if (
            Decimal(str(variant.buying_price))
            == original_buying
            and
            Decimal(str(variant.selling_price))
            == original_selling
        ):

            print(
                "PASS: ORIGINAL PRICES RESTORED"
            )

        else:

            print(
                "FAIL: ORIGINAL PRICES NOT RESTORED"
            )

    finally:

        # ==================================================
        # RESTORE SETTING
        # ==================================================

        db.session.rollback()

        settings = SystemSetting.get_settings()

        settings.auto_update_buying_price = (
            original_setting
        )

        db.session.commit()

        print(
            "AUTO-UPDATE RESTORED:",
            settings.auto_update_buying_price
        )