from decimal import Decimal

from app import create_app
from db import db
from models.purchase import Purchase
from models.product_variant import ProductVariant


app = create_app()

with app.app_context():

    variant = db.session.get(
        ProductVariant,
        384
    )

    print("VARIANT:", variant.id)
    print("SKU:", variant.sku)

    print(
        "CURRENT QUANTITY:",
        variant.quantity
    )

    print(
        "CURRENT BUYING PRICE:",
        variant.buying_price
    )

    print(
        "CURRENT SELLING PRICE:",
        variant.selling_price
    )

    # ==================================================
    # FIND ONLY OUR TWO TEST PURCHASES
    # ==================================================

    test_invoices = [
        "TEST-AUTO-UPDATE-DISABLED",
        "TEST-AUTO-UPDATE-ENABLED",
    ]

    purchases = (
        Purchase.query
        .filter(
            Purchase.invoice_number.in_(test_invoices)
        )
        .all()
    )

    print(
        "TEST PURCHASES FOUND:",
        len(purchases)
    )

    if len(purchases) != 2:
        raise Exception(
            "Expected exactly 2 test purchases. "
            "Cleanup stopped for safety."
        )

    # ==================================================
    # VERIFY ITEMS BEFORE DELETING
    # ==================================================

    total_test_quantity = 0

    for purchase in purchases:

        print(
            "PURCHASE:",
            purchase.purchase_number,
            "| INVOICE:",
            purchase.invoice_number
        )

        for item in purchase.items:

            print(
                "  ITEM VARIANT:",
                item.product_variant_id,
                "| QTY:",
                item.quantity,
                "| COST:",
                item.unit_cost
            )

            if item.product_variant_id != 384:
                raise Exception(
                    "Unexpected variant found in "
                    "test purchase. Cleanup stopped."
                )

            if item.imeis:
                raise Exception(
                    "Test purchase contains IMEIs. "
                    "Cleanup stopped for safety."
                )

            total_test_quantity += item.quantity

    print(
        "TOTAL TEST QUANTITY:",
        total_test_quantity
    )

    if total_test_quantity != 2:
        raise Exception(
            "Expected exactly 2 test units. "
            "Cleanup stopped for safety."
        )

    # ==================================================
    # REMOVE TEST STOCK
    # ==================================================

    variant.quantity -= total_test_quantity

    # ==================================================
    # RESTORE ORIGINAL PRICES
    # ==================================================

    variant.buying_price = Decimal(
        "959196.00"
    )

    variant.selling_price = Decimal(
        "1127088.00"
    )

    # ==================================================
    # DELETE TEST PURCHASES
    # ==================================================

    for purchase in purchases:

        print(
            "DELETING:",
            purchase.invoice_number
        )

        db.session.delete(purchase)

    db.session.commit()

    # ==================================================
    # VERIFY CLEANUP
    # ==================================================

    db.session.refresh(variant)

    remaining = (
        Purchase.query
        .filter(
            Purchase.invoice_number.in_(test_invoices)
        )
        .count()
    )

    print()
    print(
        "REMAINING TEST PURCHASES:",
        remaining
    )

    print(
        "FINAL QUANTITY:",
        variant.quantity
    )

    print(
        "FINAL BUYING PRICE:",
        variant.buying_price
    )

    print(
        "FINAL SELLING PRICE:",
        variant.selling_price
    )

    if remaining != 0:
        raise Exception(
            "Cleanup verification failed."
        )

    if variant.quantity != 41:
        raise Exception(
            "Quantity cleanup failed."
        )

    if (
        Decimal(str(variant.buying_price))
        != Decimal("959196.00")
    ):
        raise Exception(
            "Buying price restoration failed."
        )

    if (
        Decimal(str(variant.selling_price))
        != Decimal("1127088.00")
    ):
        raise Exception(
            "Selling price restoration failed."
        )

    print()
    print("PASS: TEST PURCHASES REMOVED")
    print("PASS: INVENTORY RESTORED")
    print("PASS: BUYING PRICE RESTORED")
    print("PASS: SELLING PRICE RESTORED")