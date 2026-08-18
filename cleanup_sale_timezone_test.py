from app import create_app
from db import db

from models.sale import Sale
from models.product_variant import ProductVariant
from models.imei import IMEI


app = create_app()

with app.app_context():

    SALE_ID = 30
    VARIANT_ID = 384
    IMEI_ID = 5608

    sale = db.session.get(
        Sale,
        SALE_ID
    )

    variant = db.session.get(
        ProductVariant,
        VARIANT_ID
    )

    imei = db.session.get(
        IMEI,
        IMEI_ID
    )

    print("SALE EXISTS:", bool(sale))
    print("VARIANT QUANTITY BEFORE:", variant.quantity)
    print("IMEI STATUS BEFORE:", imei.status)

    if not sale:
        print("SALE 30 DOES NOT EXIST.")
        raise SystemExit

    # ==========================================================
    # VERIFY THIS IS OUR TEST SALE
    # ==========================================================

    if not sale.invoice_number.startswith(
        "INV-20260817-170801-"
    ):
        raise Exception(
            "Sale 30 does not match the timezone test invoice."
        )

    # ==========================================================
    # RESTORE INVENTORY
    # ==========================================================

    variant.quantity += 1

    print(
        "VARIANT QUANTITY RESTORED TO:",
        variant.quantity
    )

    # ==========================================================
    # RESTORE IMEI
    # ==========================================================

    if imei.status == "Sold":
        imei.status = "In Stock"

    print(
        "IMEI STATUS RESTORED TO:",
        imei.status
    )

    # ==========================================================
    # DELETE SALE
    #
    # Sale.items has delete-orphan cascade.
    # Sale.payments also has delete-orphan cascade.
    # ==========================================================

    db.session.delete(sale)

    db.session.commit()

    # ==========================================================
    # VERIFY CLEANUP
    # ==========================================================

    remaining_sale = db.session.get(
        Sale,
        SALE_ID
    )

    variant = db.session.get(
        ProductVariant,
        VARIANT_ID
    )

    imei = db.session.get(
        IMEI,
        IMEI_ID
    )

    print()
    print("SALE STILL EXISTS:", bool(remaining_sale))
    print("FINAL VARIANT QUANTITY:", variant.quantity)
    print("FINAL IMEI STATUS:", imei.status)

    if remaining_sale is None:
        print("PASS: TEST SALE REMOVED")
    else:
        print("FAIL: TEST SALE STILL EXISTS")

    if variant.quantity == 41:
        print("PASS: INVENTORY RESTORED")
    else:
        print("FAIL: INVENTORY NOT RESTORED")

    if imei.status == "In Stock":
        print("PASS: IMEI RESTORED")
    else:
        print("FAIL: IMEI NOT RESTORED")