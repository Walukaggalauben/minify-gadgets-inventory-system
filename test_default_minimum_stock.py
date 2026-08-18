from app import create_app
from db import db
from models.system_setting import SystemSetting
from models.product_variant import ProductVariant
from services.product_variant_service import ProductVariantService


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()

    original_default = settings.default_minimum_stock

    temporary_variant = None

    print(
        "ORIGINAL DEFAULT MINIMUM STOCK:",
        original_default
    )

    try:

        # ==========================================
        # SET TEMPORARY SYSTEM DEFAULT
        # ==========================================

        test_default = 7

        settings.default_minimum_stock = test_default
        db.session.commit()

        print(
            "TEST DEFAULT SET TO:",
            settings.default_minimum_stock
        )

        # ==========================================
        # CREATE TEMPORARY VARIANT
        # ==========================================

        temporary_variant = ProductVariantService.create(
            {
                "product_id": 1,
                "sku": "TEST-DEFAULT-MIN-STOCK-001",
                "barcode": None,
                "storage": "TEST",
                "ram": "TEST",
                "colour": "TEST",
                "condition": "Test",
                "buying_price": 1000,
                "selling_price": 1500,
                "quantity": 10,

                # IMPORTANT:
                # minimum_stock intentionally omitted.

                "warranty_months": 0,
            }
        )

        print(
            "TEMPORARY VARIANT ID:",
            temporary_variant.id
        )

        print(
            "TEMPORARY VARIANT MINIMUM STOCK:",
            temporary_variant.minimum_stock
        )

        # ==========================================
        # VERIFY DEFAULT WAS INHERITED
        # ==========================================

        if temporary_variant.minimum_stock == test_default:

            print(
                "PASS: DEFAULT MINIMUM STOCK INHERITED"
            )

        else:

            print(
                "FAIL: DEFAULT MINIMUM STOCK NOT INHERITED"
            )

        # ==========================================
        # DELETE TEMPORARY VARIANT
        # ==========================================

        db.session.delete(temporary_variant)
        db.session.commit()

        print(
            "PASS: TEMPORARY VARIANT DELETED"
        )

        temporary_variant = None

    finally:

        # ==========================================
        # CLEANUP IF NECESSARY
        # ==========================================

        if temporary_variant is not None:

            db.session.delete(
                temporary_variant
            )

        # ==========================================
        # RESTORE ORIGINAL SETTING
        # ==========================================

        settings.default_minimum_stock = (
            original_default
        )

        db.session.commit()

        print(
            "DEFAULT MINIMUM STOCK RESTORED:",
            settings.default_minimum_stock
        )