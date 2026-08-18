from app import create_app
from db import db
from models.system_setting import SystemSetting
from models.product_variant import ProductVariant
from services.sale_service import SaleService


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()

    original_customer_required = settings.require_customer_on_sale
    original_negative_stock = settings.prevent_negative_stock
    original_price_override = settings.allow_price_override

    variant = db.session.get(ProductVariant, 463)

    if not variant:
        raise Exception("Test variant 463 was not found.")

    original_quantity = variant.quantity

    print("TEST VARIANT:", variant.id)
    print("TEST SKU:", variant.sku)
    print("ORIGINAL QUANTITY:", original_quantity)

    print(
        "ORIGINAL CUSTOMER REQUIRED:",
        original_customer_required
    )

    print(
        "ORIGINAL NEGATIVE STOCK:",
        original_negative_stock
    )

    try:

        # Isolate the negative-stock setting.
        settings.require_customer_on_sale = False
        settings.allow_price_override = False
        settings.prevent_negative_stock = True

        db.session.commit()

        print("CUSTOMER REQUIREMENT TEMPORARILY DISABLED")
        print("PRICE OVERRIDE DISABLED")
        print("NEGATIVE STOCK PROTECTION ENABLED")

        # ==========================================
        # TEST — SELL MORE THAN AVAILABLE STOCK
        # ==========================================

        attempted_quantity = original_quantity + 1

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
                        "quantity": attempted_quantity,
                        "price": str(variant.selling_price),
                        "price_override": False,
                    }
                ],
            )

            print(
                "FAIL: NEGATIVE STOCK WAS ALLOWED"
            )

        except Exception as error:

            print(
                "SALE REJECTED WITH:",
                str(error)
            )

            if "Insufficient stock" in str(error):

                print(
                    "PASS: NEGATIVE STOCK BLOCKED"
                )

            else:

                print(
                    "FAIL: WRONG VALIDATION REJECTED THE SALE"
                )

        # ==========================================
        # VERIFY INVENTORY WAS NOT CHANGED
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

    finally:

        # ==========================================
        # RESTORE ORIGINAL SETTINGS
        # ==========================================

        settings.require_customer_on_sale = (
            original_customer_required
        )

        settings.prevent_negative_stock = (
            original_negative_stock
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
            "NEGATIVE STOCK RESTORED:",
            settings.prevent_negative_stock
        )

        print(
            "PRICE OVERRIDE RESTORED:",
            settings.allow_price_override
        )