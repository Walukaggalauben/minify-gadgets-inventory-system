from decimal import Decimal

from db import db

from models.sale import Sale
from models.sale_item import SaleItem
from models.product_variant import ProductVariant
from models.imei import IMEI


class SaleService:

    @staticmethod
    def create_sale(
        invoice_number,
        customer_name,
        customer_phone,
        payment_method,
        created_by,
        items
    ):

        sale = Sale(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_phone=customer_phone,
            payment_method=payment_method,
            created_by=created_by
        )

        db.session.add(sale)

        total_amount = Decimal("0.00")
        total_profit = Decimal("0.00")

        for item in items:

            variant = ProductVariant.query.get(
                item["variant_id"]
            )

            if not variant:
                raise Exception("Product Variant not found.")

            quantity = int(item["quantity"])

            if quantity <= 0:
                raise Exception("Invalid quantity.")

            if variant.quantity < quantity:
                raise Exception(
                    f"Not enough stock for {variant.sku}"
                )

            # Deduct stock
            variant.quantity -= quantity

            line_total = (
                Decimal(str(variant.selling_price))
                * quantity
            )

            line_profit = (
                (
                    Decimal(str(variant.selling_price))
                    - Decimal(str(variant.buying_price))
                )
                * quantity
            )

            sale_item = SaleItem(

                sale=sale,

                product_variant_id=variant.id,

                quantity=quantity,

                buying_price=variant.buying_price,

                selling_price=variant.selling_price,

                total=line_total,

                profit=line_profit

            )

            # IMEI (optional)

            if item.get("imei_id"):

                imei = IMEI.query.get(
                    item["imei_id"]
                )

                if imei:

                    imei.status = "Sold"

                    sale_item.imei = imei

            db.session.add(sale_item)

            total_amount += line_total

            total_profit += line_profit

        sale.total_amount = total_amount

        sale.profit = total_profit

        db.session.commit()

        return sale