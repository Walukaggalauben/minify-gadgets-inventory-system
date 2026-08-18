from app import create_app
from db import db
from models.system_setting import SystemSetting
from models.product_variant import ProductVariant
from services.sale_service import SaleService


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()

    original_customer_required = settings.require_customer_on_sale
    original_price_override = settings.allow_price_override

    variant = ProductVariant.query.get(384)

    if not variant:
        raise Exception("Test variant 384 was not found.")

    original_quantity = variant.quantity

    print("TEST VARIANT:", variant.id)
    print("TEST SKU:", variant.sku)
    print("ORIGINAL QUANTITY:", original_quantity)

    print(
        "ORIGINAL CUSTOMER REQUIRED:",
        original_customer_required
    )

    print(
        "ORIGINAL PRICE OVERRIDE:",
        original_price_override
    )

    try:

        # Disable customer requirement so we can
        # isolate the price-override rule.
        settings.require_customer_on_sale = False
        settings.allow_price_override = False

        db.session.commit()

        print("CUSTOMER REQUIREMENT TEMPORARILY DISABLED")
        print("PRICE OVERRIDE DISABLED")

        # ==========================================
        # TEST PRICE OVERRIDE BLOCK
        # ==========================================

        try:

            SaleService.create_sale(
                customer_id=None,
                customer_name="",
                customer_phone="",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "price": "1",
                        "price_override": True,
                    }
                ],
            )

            print(
                "FAIL: PRICE OVERRIDE WAS ALLOWED"
            )

        except Exception as error:

            print("SALE REJECTED WITH:", str(error))

            if (
                "Price override is not allowed"
                in str(error)
            ):
                print(
                    "PASS: PRICE OVERRIDE BLOCKED"
                )
            else:
                print(
                    "FAIL: WRONG VALIDATION REJECTED THE SALE"
                )

        # ==========================================
        # VERIFY STOCK WAS NOT CHANGED
        # ==========================================

        db.session.expire_all()

        variant_after = db.session.get(
            ProductVariant,
            variant.id
        )

        print(
            "QUANTITY AFTER TEST:",
            variant_after.quantity
        )

        if variant_after.quantity == original_quantity:
            print(
                "PASS: INVENTORY QUANTITY UNCHANGED"
            )
        else:
            print(
                "FAIL: INVENTORY QUANTITY CHANGED"
            )

        # ==========================================
        # TEST SETTING ENABLE
        # ==========================================

        settings.allow_price_override = True
        db.session.commit()

        if settings.allow_price_override:
            print(
                "PASS: PRICE OVERRIDE SETTING ENABLED"
            )
        else:
            print(
                "FAIL: PRICE OVERRIDE SETTING DID NOT ENABLE"
            )

    finally:

        settings.require_customer_on_sale = (
            original_customer_required
        )

        settings.allow_price_override = (
            original_price_override
        )

        db.session.commit()

        print(
            "CUSTOMER REQUIREMENT RESTORED:",
            settings.require_customer_on_sale
        )

        print(
            "PRICE OVERRIDE RESTORED:",
            settings.allow_price_override
        )