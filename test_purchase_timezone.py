from decimal import Decimal
from datetime import datetime

from app import create_app
from db import db

from models.product_variant import ProductVariant
from models.imei import IMEI
from models.purchase import Purchase
from utils.timezone import application_now
from services.purchase_service import PurchaseService


app = create_app()

with app.app_context():

    variant = db.session.get(ProductVariant, 384)

    original_quantity = variant.quantity

    # Find an unused test IMEI number
    test_imei = "TEST-TZ-072226133861923"

    # Make sure it does not already exist
    existing = IMEI.query.filter_by(imei=test_imei).first()

    if existing:
        raise Exception(
            f"Test IMEI already exists: {test_imei}"
        )

    before = application_now()

    print("TEST VARIANT:", variant.id)
    print("TEST SKU:", variant.sku)
    print("ORIGINAL QUANTITY:", original_quantity)
    print("APPLICATION TIME BEFORE:", before)
    print("TEST IMEI:", test_imei)

    purchase = None

    try:

        purchase = PurchaseService.create_purchase(
            supplier_id=1,
            purchase_date=before.date(),
            invoice_number="TEST-TIMEZONE-PURCHASE",
            payment_method="Cash",
            notes="AUTOMATED TIMEZONE TEST",
            created_by=1,
            items=[
                {
                    "product_variant_id": variant.id,
                    "quantity": 1,
                    "unit_cost": Decimal(
                        str(variant.buying_price)
                    ),
                    "default_selling_price": Decimal(
                        str(variant.selling_price)
                    ),
                    "imeis": [test_imei],
                }
            ],
        )

        after = application_now()

        db.session.refresh(variant)

        created_imei = IMEI.query.filter_by(
            imei=test_imei
        ).first()

        print("TEST PURCHASE ID:", purchase.id)
        print(
            "PURCHASE NUMBER:",
            purchase.purchase_number
        )
        print(
            "PURCHASE DATE:",
            purchase.purchase_date
        )

        print(
            "IMEI RECEIVED DATE:",
            created_imei.received_date
        )

        print("APPLICATION TIME AFTER:", after)

        # ==================================================
        # VERIFY PURCHASE DATE
        # ==================================================

        if purchase.purchase_date == before.date():

            print(
                "PASS: PURCHASE DATE USES APPLICATION DATE"
            )

        else:

            print(
                "FAIL: PURCHASE DATE DOES NOT MATCH "
                "APPLICATION DATE"
            )

               # ==================================================
        # VERIFY IMEI RECEIVED DATE
        # ==================================================

        received = created_imei.received_date

        before_naive = before.replace(
            tzinfo=None,
            microsecond=0
        )

        after_naive = after.replace(
            tzinfo=None,
            microsecond=0
        )

        if before_naive <= received <= after_naive:

            print(
                "PASS: IMEI RECEIVED DATE USES "
                "APPLICATION TIME"
            )

        else:

            print(
                "FAIL: IMEI RECEIVED DATE OUTSIDE "
                "APPLICATION TIME WINDOW"
            )

        # ==================================================
        # VERIFY INVENTORY
        # ==================================================

        print(
            "QUANTITY DURING TEST:",
            variant.quantity
        )

        if variant.quantity == original_quantity + 1:

            print(
                "PASS: INVENTORY INCREASED FOR "
                "TEST PURCHASE"
            )

        else:

            print(
                "FAIL: INVENTORY QUANTITY "
                "DID NOT INCREASE"
            )

    except Exception as e:

        print(
            "UNEXPECTED ERROR:",
            str(e)
        )

    finally:

        # ==================================================
        # CLEANUP
        # ==================================================

        db.session.rollback()

        test_purchase = Purchase.query.filter_by(
            invoice_number="TEST-TIMEZONE-PURCHASE"
        ).first()

        if test_purchase:

            test_purchase_id = test_purchase.id

            test_items = list(
                test_purchase.items
            )

            for item in test_items:

                test_variant = db.session.get(
                    ProductVariant,
                    item.product_variant_id
                )

                if test_variant:

                    test_variant.quantity -= item.quantity

            test_imeis = IMEI.query.filter_by(
                purchase_item_id=(
                    test_items[0].id
                    if test_items
                    else None
                )
            ).all()

            for imei in test_imeis:

                db.session.delete(imei)

            db.session.delete(test_purchase)

            db.session.commit()

            print(
                "TEST PURCHASE REMOVED:",
                test_purchase_id
            )

        else:

            print(
                "NO TEST PURCHASE FOUND FOR CLEANUP"
            )

        variant = db.session.get(
            ProductVariant,
            384
        )

        remaining_imei = IMEI.query.filter_by(
            imei=test_imei
        ).first()

        print(
            "FINAL QUANTITY:",
            variant.quantity
        )

        print(
            "TEST IMEI EXISTS:",
            bool(remaining_imei)
        )

        if variant.quantity == original_quantity:

            print(
                "PASS: INVENTORY RESTORED"
            )

        else:

            print(
                "FAIL: INVENTORY NOT RESTORED"
            )

        if remaining_imei is None:

            print(
                "PASS: TEST IMEI REMOVED"
            )

        else:

            print(
                "FAIL: TEST IMEI STILL EXISTS"
            )