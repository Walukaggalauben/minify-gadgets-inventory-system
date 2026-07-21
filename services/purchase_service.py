from decimal import Decimal
from datetime import datetime

from db import db

from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.product_variant import ProductVariant


class PurchaseService:

    @staticmethod
    def generate_purchase_number():
        """
        Generates:
        PUR-2026-000001
        """

        year = datetime.now().year

        last_purchase = (
            Purchase.query
            .order_by(Purchase.id.desc())
            .first()
        )

        if last_purchase:
            try:
                last_number = int(
                    last_purchase.purchase_number.split("-")[-1]
                )
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        next_number = last_number + 1

        return f"PUR-{year}-{next_number:06d}"

    @staticmethod
    def create_purchase(
        supplier_id,
        purchase_date,
        invoice_number,
        payment_method,
        notes,
        created_by,
        items
    ):
        """
        items example:

        [
            {
                "product_variant_id": 1,
                "quantity": 5,
                "unit_cost": 2000000
            },
            ...
        ]
        """

        try:

            purchase = Purchase(
                purchase_number=PurchaseService.generate_purchase_number(),
                supplier_id=supplier_id,
                purchase_date=purchase_date,
                invoice_number=invoice_number,
                payment_method=payment_method,
                notes=notes,
                created_by=created_by,
                status="Received",
                total_amount=Decimal("0.00")
            )

            db.session.add(purchase)
            db.session.flush()

            total = Decimal("0.00")

            for item in items:

                variant = ProductVariant.query.get(
                    item["product_variant_id"]
                )

                if not variant:
                    raise Exception("Product Variant not found.")

                quantity = int(item["quantity"])

                unit_cost = Decimal(
                    str(item["unit_cost"])
                )

                subtotal = unit_cost * quantity

                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_variant_id=variant.id,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    subtotal=subtotal
                )

                db.session.add(purchase_item)

                # Update Stock
                variant.quantity += quantity

                total += subtotal

            purchase.total_amount = total

            db.session.commit()

            return purchase

        except Exception as e:

            db.session.rollback()

            raise e