from decimal import Decimal
from datetime import datetime

from db import db

from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.product_variant import ProductVariant
from models.imei import IMEI


class PurchaseService:

    @staticmethod
    def generate_purchase_number():

        year = datetime.now().year

        last_purchase = Purchase.query.order_by(Purchase.id.desc()).first()

        if last_purchase:

            try:

                last_number = int(last_purchase.purchase_number.split("-")[-1])

            except Exception:

                last_number = 0

        else:

            last_number = 0

        return f"PUR-{year}-{last_number + 1:06d}"

    # ============================================================
    # CREATE PURCHASE
    # ============================================================

    @staticmethod
    def create_purchase(
        supplier_id,
        purchase_date,
        invoice_number,
        payment_method,
        notes,
        created_by,
        items,
    ):

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
                total_amount=Decimal("0.00"),
            )

            db.session.add(purchase)

            db.session.flush()

            grand_total = Decimal("0.00")

            for item in items:

                variant = ProductVariant.query.get(item["product_variant_id"])

                if not variant:
                    raise Exception("Product Variant not found.")

                quantity = int(item["quantity"])

                buying_price = Decimal(str(item["unit_cost"]))

                selling_price = Decimal(
                    str(item.get("default_selling_price", variant.selling_price))
                )

                imeis = item.get("imeis", [])

                if len(imeis) != quantity:

                    raise Exception(
                        f"{variant.product.name}: Quantity and IMEI count do not match."
                    )

                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_variant_id=variant.id,
                    quantity=quantity,
                    unit_cost=buying_price,
                    subtotal=buying_price * quantity,
                )

                db.session.add(purchase_item)

                variant.quantity += quantity

                grand_total += buying_price * quantity

                # ==========================================
                # CREATE IMEIs
                # ==========================================

                for imei_number in imeis:

                    imei_number = imei_number.strip()

                    if not imei_number:
                        continue

                    exists = IMEI.query.filter_by(imei=imei_number).first()

                    if exists:

                        raise Exception(f"IMEI already exists: {imei_number}")

                    new_imei = IMEI(
                        product_variant_id=variant.id,
                        imei=imei_number,
                        buying_price=buying_price,
                        default_selling_price=selling_price,
                        acquisition_source="Purchase",
                        received_date=datetime.utcnow(),
                        status="In Stock",
                    )

                    db.session.add(new_imei)

            purchase.total_amount = grand_total

            db.session.commit()

            return purchase

        except Exception as e:

            db.session.rollback()

            raise e
