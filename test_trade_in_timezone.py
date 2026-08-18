from decimal import Decimal

from app import create_app
from db import db

from models.product_variant import ProductVariant
from models.imei import IMEI
from models.trade_in import TradeIn
from utils.timezone import application_now
from services.trade_in_service import TradeInService


app = create_app()

with app.app_context():

    variant = db.session.get(ProductVariant, 384)

    original_quantity = variant.quantity

    test_imei = "TEST-TRD-TZ-072226133861924"

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

    try:

        trade = TradeInService.create_trade_in(
            customer_id=1,
            customer_data={
                "customer_name": "JOHN DOE",
                "phone_number": "0700123456",
                "trade_in_date": before.date(),
                "cash_paid": 0,
                "topup_received": 0,
                "notes": "AUTOMATED TIMEZONE TEST",
            },
            items=[
                {
                    "product_variant_id": variant.id,
                    "final_trade_value": Decimal(
                        str(variant.buying_price)
                    ),
                    "default_selling_price": Decimal(
                        str(variant.selling_price)
                    ),
                    "offered_value": Decimal(
                        str(variant.buying_price)
                    ),
                    "imei": test_imei,
                }
            ],
            created_by=1,
        )

        after = application_now()

        db.session.refresh(variant)

        created_imei = IMEI.query.filter_by(
            imei=test_imei
        ).first()

        print("TEST TRADE-IN ID:", trade.id)
        print(
            "TRADE-IN NUMBER:",
            trade.trade_in_number
        )
        print(
            "TRADE-IN DATE:",
            trade.trade_in_date
        )
        print(
            "IMEI RECEIVED DATE:",
            created_imei.received_date
        )
        print(
            "APPLICATION TIME AFTER:",
            after
        )

        # ==================================================
        # VERIFY TRADE-IN DATE
        # ==================================================

        if trade.trade_in_date == before.date():

            print(
                "PASS: TRADE-IN DATE USES "
                "APPLICATION DATE"
            )

        else:

            print(
                "FAIL: TRADE-IN DATE DOES NOT MATCH "
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
                "TEST TRADE-IN"
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

        test_trade = TradeIn.query.filter_by(
            trade_in_number=(
                trade.trade_in_number
                if "trade" in locals() and trade
                else None
            )
        ).first()

        if test_trade:

            test_trade_id = test_trade.id

            test_imeis = IMEI.query.filter_by(
                imei=test_imei
            ).all()

            for imei in test_imeis:
                db.session.delete(imei)

            db.session.delete(test_trade)

            db.session.flush()

            variant = db.session.get(
                ProductVariant,
                384
            )

            variant.quantity = original_quantity

            db.session.commit()

            print(
                "TEST TRADE-IN REMOVED:",
                test_trade_id
            )

        else:

            # Safety cleanup if the trade-in was created
            # but could not be located by its number.
            test_imeis = IMEI.query.filter_by(
                imei=test_imei
            ).all()

            for imei in test_imeis:
                db.session.delete(imei)

            variant = db.session.get(
                ProductVariant,
                384
            )

            variant.quantity = original_quantity

            db.session.commit()

            print(
                "NO TEST TRADE-IN FOUND; "
                "SAFETY CLEANUP COMPLETED"
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