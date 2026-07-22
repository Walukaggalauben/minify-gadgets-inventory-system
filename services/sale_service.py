from datetime import datetime
from decimal import Decimal

from db import db



from models.sale import Sale
from models.sale_item import SaleItem
from models.product_variant import ProductVariant
from models.imei import IMEI


class SaleService:

    @staticmethod
    def generate_invoice_number():
        """
        Generates a unique invoice number.

        Example:
        INV-20260722-153045
        """
        return datetime.now().strftime("INV-%Y%m%d-%H%M%S")

    @staticmethod
    def create_sale(
        customer_name,
        customer_phone,
        payment_method,
        created_by,
        items
    ):

        try:

            sale = Sale(

                invoice_number=SaleService.generate_invoice_number(),

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
                    int(item["variant_id"])
                )

                if not variant:
                    raise Exception(
                        "Selected product variant does not exist."
                    )

                quantity = int(item["quantity"])

                if quantity <= 0:
                    raise Exception(
                        "Quantity must be greater than zero."
                    )

                if variant.quantity < quantity:
                    raise Exception(
                        f"Insufficient stock for {variant.sku}."
                    )

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

                    product_variant_id=variant.id,

                    quantity=quantity,

                    buying_price=variant.buying_price,

                    selling_price=variant.selling_price,

                    total=line_total,

                    profit=line_profit

                )

                db.session.add(sale_item)

                sale_item.sale = sale

                imei_id = item.get("imei_id")

                if imei_id:

                    imei = IMEI.query.get(int(imei_id))

                    if not imei:
                        raise Exception(
                            "Selected IMEI was not found."
                        )

                    if imei.status == "Sold":
                        raise Exception(
                            "This IMEI has already been sold."
                        )

                    if imei.product_variant_id != variant.id:
                        raise Exception(
                            "Selected IMEI does not belong to the selected product."
                        )

                    imei.status = "Sold"

                    sale_item.imei = imei

                variant.quantity -= quantity

                

                total_amount += line_total
                total_profit += line_profit

            sale.total_amount = total_amount
            sale.profit = total_profit

            db.session.commit()

            return sale

        except Exception:

            db.session.rollback()

            raise