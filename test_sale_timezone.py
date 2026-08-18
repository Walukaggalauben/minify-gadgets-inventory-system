from app import create_app
from db import db

from models.sale import Sale
from models.product_variant import ProductVariant
from models.customer import Customer
from models.imei import IMEI

from services.sale_service import SaleService
from utils.timezone import application_now


app = create_app()

with app.app_context():

    VARIANT_ID = 384
    CUSTOMER_ID = 1
    IMEI_ID = 5608
    CREATED_BY = 1

    variant = db.session.get(
        ProductVariant,
        VARIANT_ID
    )

    customer = db.session.get(
        Customer,
        CUSTOMER_ID
    )

    imei = db.session.get(
        IMEI,
        IMEI_ID
    )

    original_quantity = variant.quantity
    original_imei_status = imei.status

    print("TEST VARIANT:", variant.id)
    print("TEST SKU:", variant.sku)
    print("ORIGINAL QUANTITY:", original_quantity)
    print("ORIGINAL IMEI STATUS:", original_imei_status)

    sale = None

    try:

        # ======================================================
        # CAPTURE APPLICATION TIME
        # ======================================================

        before = application_now()

        print(
            "APPLICATION TIME BEFORE:",
            before
        )

        # ======================================================
        # CREATE TEST SALE
        # ======================================================

        sale = SaleService.create_sale(
            customer_id=customer.id,
            customer_name=customer.full_name,
            customer_phone=customer.phone,
            payment_method="Cash",
            created_by=CREATED_BY,
            items=[
                {
                    "variant_id": variant.id,
                    "quantity": 1,
                    "price_override": False,
                    "imei_id": imei.id,
                }
            ],
            amount_paid=variant.selling_price,
            payment_currency="UGX",
        )

        print(
            "TEST SALE ID:",
            sale.id
        )

        print(
            "TEST INVOICE:",
            sale.invoice_number
        )

        print(
            "STORED SALE DATE:",
            sale.sale_date
        )

        after = application_now()

        print(
            "APPLICATION TIME AFTER:",
            after
        )

        # ======================================================
        # VERIFY SALE DATE
        # ======================================================

        stored_sale_time = sale.sale_date

        expected_start = before.replace(
            tzinfo=None,
            microsecond=0,
        )

        expected_end = after.replace(
            tzinfo=None,
            microsecond=0,
        )

        stored_second = stored_sale_time.replace(
            microsecond=0
        )

        if (
            expected_start
            <= stored_second
            <= expected_end
        ):
            print(
                "PASS: SALE DATE USES APPLICATION TIME"
            )
        else:
            print(
                "FAIL: SALE DATE OUTSIDE "
                "APPLICATION TIME WINDOW"
            )

        # ======================================================
        # VERIFY INVOICE DATE
        # ======================================================

        expected_date = before.strftime(
            "%Y%m%d"
        )

        if sale.invoice_number.startswith(
            f"INV-{expected_date}-"
        ):
            print(
                "PASS: INVOICE USES APPLICATION DATE"
            )
        else:
            print(
                "FAIL: INVOICE DATE DOES NOT "
                "MATCH APPLICATION DATE"
            )

        # ======================================================
        # VERIFY INVENTORY
        # ======================================================

        variant = db.session.get(
            ProductVariant,
            VARIANT_ID
        )

        print(
            "QUANTITY DURING TEST:",
            variant.quantity
        )

        if variant.quantity == (
            original_quantity - 1
        ):
            print(
                "PASS: INVENTORY REDUCED "
                "FOR TEST SALE"
            )
        else:
            print(
                "FAIL: INVENTORY WAS NOT "
                "REDUCED CORRECTLY"
            )

        # ======================================================
        # VERIFY IMEI
        # ======================================================

        imei = db.session.get(
            IMEI,
            IMEI_ID
        )

        print(
            "IMEI STATUS DURING TEST:",
            imei.status
        )

        if imei.status == "Sold":
            print(
                "PASS: IMEI MARKED SOLD"
            )
        else:
            print(
                "FAIL: IMEI NOT MARKED SOLD"
            )

    finally:

        # ======================================================
        # CLEAN UP COMMITTED TEST SALE
        # ======================================================

        if sale is not None:

            test_sale_id = sale.id

            sale_to_delete = db.session.get(
                Sale,
                test_sale_id
            )

            if sale_to_delete:

                db.session.delete(
                    sale_to_delete
                )

                db.session.flush()

            # Restore inventory.
            variant = db.session.get(
                ProductVariant,
                VARIANT_ID
            )

            variant.quantity = (
                original_quantity
            )

            # Restore IMEI.
            imei = db.session.get(
                IMEI,
                IMEI_ID
            )

            imei.status = (
                original_imei_status
            )

            db.session.commit()

        # ======================================================
        # FINAL VERIFICATION
        # ======================================================

        variant = db.session.get(
            ProductVariant,
            VARIANT_ID
        )

        imei = db.session.get(
            IMEI,
            IMEI_ID
        )

        remaining_sale = (
            db.session.get(
                Sale,
                sale.id
            )
            if sale is not None
            else None
        )

        print(
            "FINAL QUANTITY:",
            variant.quantity
        )

        print(
            "FINAL IMEI STATUS:",
            imei.status
        )

        print(
            "TEST SALE STILL EXISTS:",
            bool(remaining_sale)
        )

        if variant.quantity == original_quantity:
            print(
                "PASS: INVENTORY RESTORED"
            )
        else:
            print(
                "FAIL: INVENTORY NOT RESTORED"
            )

        if imei.status == original_imei_status:
            print(
                "PASS: IMEI RESTORED"
            )
        else:
            print(
                "FAIL: IMEI NOT RESTORED"
            )

        if remaining_sale is None:
            print(
                "PASS: TEST SALE REMOVED"
            )
        else:
            print(
                "FAIL: TEST SALE STILL EXISTS"
            )