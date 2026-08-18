from decimal import Decimal

from app import create_app
from db import db

from models.system_setting import SystemSetting
from models.product_variant import ProductVariant
from models.customer import Customer
from models.sale import Sale

from services.sale_service import SaleService


app = create_app()

with app.app_context():

    variant = db.session.get(ProductVariant, 384)
    customer = Customer.query.filter_by(is_active=True).first()
    settings = SystemSetting.get_settings()

    original_setting = settings.require_customer_on_sale
    original_quantity = variant.quantity

    print("TEST VARIANT:", variant.id)
    print("TEST SKU:", variant.sku)
    print("ORIGINAL QUANTITY:", original_quantity)
    print("ORIGINAL REQUIRE CUSTOMER:", original_setting)
    print("TEST CUSTOMER:", customer.id, customer.full_name)

    try:

        # ==================================================
        # TEST 1: SETTING DISABLED
        # ==================================================

        settings.require_customer_on_sale = False
        db.session.commit()

        print("REQUIRE CUSTOMER DISABLED")

        try:

            sale = SaleService.create_sale(
                customer_id=None,
                customer_name="TEST WALK-IN",
                customer_phone="0700000000",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "price": Decimal(str(variant.selling_price)),
                        "price_override": False,
                    }
                ],
                amount_paid=Decimal(str(variant.selling_price)),
                payment_currency="UGX",
            )

            print("SALE WITHOUT CUSTOMER ID:", sale.id)
            print("PASS: SALE ALLOWED WHEN CUSTOMER REQUIREMENT DISABLED")

        except Exception as e:

            print(
                "FAIL: SALE REJECTED WHEN CUSTOMER REQUIREMENT DISABLED:",
                str(e),
            )

        # --------------------------------------------------
        # Remove test sale
        # --------------------------------------------------

        db.session.rollback()

        test_sale = (
            Sale.query
            .order_by(Sale.id.desc())
            .first()
        )

        if test_sale and test_sale.customer_name == "TEST WALK-IN":
            db.session.delete(test_sale)
            db.session.commit()

        variant = db.session.get(ProductVariant, 384)

        # Restore inventory if necessary
        if variant.quantity != original_quantity:
            variant.quantity = original_quantity
            db.session.commit()

        # ==================================================
        # TEST 2: SETTING ENABLED
        # ==================================================

        settings = SystemSetting.get_settings()
        settings.require_customer_on_sale = True
        db.session.commit()

        print("REQUIRE CUSTOMER ENABLED")

        try:

            SaleService.create_sale(
                customer_id=None,
                customer_name="TEST WALK-IN",
                customer_phone="0700000000",
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "price": Decimal(str(variant.selling_price)),
                        "price_override": False,
                    }
                ],
                amount_paid=Decimal(str(variant.selling_price)),
                payment_currency="UGX",
            )

            print(
                "FAIL: SALE WITHOUT CUSTOMER WAS ALLOWED "
                "WHEN REQUIREMENT ENABLED"
            )

            db.session.rollback()

        except Exception as e:

            print("EXPECTED ERROR:", str(e))

            if "customer is required" in str(e).lower():

                print(
                    "PASS: SALE BLOCKED WHEN CUSTOMER "
                    "REQUIREMENT ENABLED"
                )

            else:

                print(
                    "FAIL: WRONG ERROR WHEN CUSTOMER "
                    "REQUIREMENT ENABLED"
                )

            db.session.rollback()

        # ==================================================
        # TEST 3: VALID CUSTOMER
        # ==================================================

        variant = db.session.get(ProductVariant, 384)

        print("TESTING SALE WITH VALID CUSTOMER")

        try:

            sale = SaleService.create_sale(
                customer_id=customer.id,
                customer_name=customer.full_name,
                customer_phone=customer.phone,
                payment_method="Cash",
                created_by=1,
                items=[
                    {
                        "variant_id": variant.id,
                        "quantity": 1,
                        "price": Decimal(str(variant.selling_price)),
                        "price_override": False,
                    }
                ],
                amount_paid=Decimal(str(variant.selling_price)),
                payment_currency="UGX",
            )

            print("CUSTOMER SALE ID:", sale.id)

            if sale.customer_id == customer.id:

                print(
                    "PASS: SALE WITH VALID CUSTOMER "
                    "ALLOWED"
                )

            else:

                print(
                    "FAIL: SALE CUSTOMER ID INCORRECT"
                )

        except Exception as e:

            print(
                "FAIL: SALE WITH VALID CUSTOMER "
                "WAS REJECTED:",
                str(e),
            )

        # --------------------------------------------------
        # Cleanup customer test sale
        # --------------------------------------------------

        db.session.rollback()

        test_sales = (
            Sale.query
            .filter(Sale.customer_id == customer.id)
            .order_by(Sale.id.desc())
            .all()
        )

        for sale in test_sales:

            if sale.id:

                # Only remove the most recent sale created
                # by this test if it affected inventory.
                if sale.customer_name == customer.full_name:
                    db.session.delete(sale)
                    break

        db.session.commit()

        variant = db.session.get(ProductVariant, 384)

        if variant.quantity != original_quantity:
            variant.quantity = original_quantity
            db.session.commit()

    finally:

        # ==================================================
        # RESTORE ORIGINAL SETTING
        # ==================================================

        db.session.rollback()

        settings = SystemSetting.get_settings()
        settings.require_customer_on_sale = original_setting
        db.session.commit()

        variant = db.session.get(ProductVariant, 384)

        print(
            "FINAL QUANTITY:",
            variant.quantity
        )

        print(
            "REQUIRE CUSTOMER RESTORED:",
            settings.require_customer_on_sale
        )

        if variant.quantity == original_quantity:
            print("PASS: INVENTORY RESTORED")
        else:
            print("FAIL: INVENTORY NOT RESTORED")