from datetime import datetime
from decimal import Decimal, InvalidOperation

from db import db

from models.sale import Sale
from models.customer import Customer
from models.sale_item import SaleItem
from models.product_variant import ProductVariant
from models.imei import IMEI
from models.system_setting import SystemSetting
from models.sale_payment import SalePayment


class SaleService:

    # ==========================================================
    # INVOICE NUMBER
    # ==========================================================

    @staticmethod
    def generate_invoice_number():
        """
        Generate a unique invoice number.

        Example:
        INV-20260728-183045
        """
        return datetime.now().strftime("INV-%Y%m%d-%H%M%S-%f")[:-3]

    # ==========================================================
    # CREATE SALE
    # ==========================================================

    @staticmethod
    def create_sale(
        customer_id,
        customer_name,
        customer_phone,
        payment_method,
        created_by,
        items,
        amount_paid=None,
        due_date=None,
        payment_reference=None,
        payment_notes=None,
    ):

        try:

            # ==================================================
            # SYSTEM SETTINGS
            # ==================================================

            settings = SystemSetting.get_settings()

            # ==================================================
            # CUSTOMER VALIDATION
            # ==================================================

            customer = None

            if customer_id:

                customer = Customer.query.get(int(customer_id))

                if not customer:

                    raise Exception("Selected customer was not found.")

                customer_name = customer.full_name

                customer_phone = customer.phone

            if settings.require_customer_on_sale:

                if not customer_name or not customer_name.strip():

                    raise Exception("Customer name is required for this sale.")

            if not customer_phone:
                customer_phone = customer.phone if customer else ""

            if settings.require_customer_on_sale and (not customer_phone or not customer_phone.strip()):
                raise Exception("Customer phone number is required when customer details are required.")

            # ==================================================
            # CART VALIDATION
            # ==================================================

            if not items:
                raise Exception("No items have been added to the sale.")

            # ==================================================
            # CREATE SALE
            # ==================================================

            sale = Sale(
                invoice_number=SaleService.generate_invoice_number(),
                customer_id=customer.id if customer else None,
                customer_name=customer_name,
                customer_phone=customer_phone,
                payment_method=payment_method,
                created_by=created_by,
                amount_paid=Decimal("0.00"),
                balance_due=Decimal("0.00"),
                payment_status="Paid",
                due_date=due_date,
            )
            db.session.add(sale)

            # ==================================================
            # SALE TOTALS
            # ==================================================

            total_amount = Decimal("0.00")
            total_profit = Decimal("0.00")

            # ==================================================
            # PROCESS CART ITEMS
            # ==================================================

            for item in items:

                # --------------------------------------------------
                # VARIANT
                # --------------------------------------------------

                variant_id = item.get("variant_id")

                if not variant_id:
                    raise Exception("Product variant is missing.")

                variant = ProductVariant.query.get(int(variant_id))

                if not variant:
                    raise Exception("Selected product variant does not exist.")

                # --------------------------------------------------
                # QUANTITY
                # --------------------------------------------------

                try:
                    quantity = int(item.get("quantity", 1))

                except (ValueError, TypeError):
                    raise Exception(f"Invalid quantity for {variant.sku}.")

                if quantity <= 0:
                    raise Exception("Quantity must be greater than zero.")

                # --------------------------------------------------
                # STOCK VALIDATION
                # --------------------------------------------------

                if settings.prevent_negative_stock and variant.quantity < quantity:
                    raise Exception(
                        f"Insufficient stock for {variant.sku}. "
                        f"Only {variant.quantity} item(s) available."
                    )

                # ==================================================
                # SELLING PRICE
                # ==================================================

                standard_price = Decimal(str(variant.selling_price))

                # For an individually tracked device, its stored selling price is
                # the default price and its own acquisition cost is the true cost.
                selected_imei_id = item.get("imei_id")
                selected_imei_obj = None
                if selected_imei_id:
                    selected_imei_obj = IMEI.query.get(int(selected_imei_id))
                    if not selected_imei_obj:
                        raise Exception("Selected IMEI was not found.")
                    if selected_imei_obj.status != "In Stock":
                        raise Exception("Selected IMEI is not available.")
                    if selected_imei_obj.product_variant_id != variant.id:
                        raise Exception("Selected IMEI does not belong to the selected product.")

                    if selected_imei_obj.default_selling_price is not None:
                        standard_price = Decimal(str(selected_imei_obj.default_selling_price))

                submitted_price = item.get("price")

                price_override_requested = bool(item.get("price_override", False))

                # --------------------------------------------------
                # NORMAL SALE
                # --------------------------------------------------
                #
                # Cashier did NOT click Negotiated Price.
                #
                # Ignore whatever price may have been sent from
                # the browser and use the database variant price.
                # --------------------------------------------------

                if not price_override_requested:

                    actual_selling_price = standard_price

                # --------------------------------------------------
                # NEGOTIATED SALE
                # --------------------------------------------------
                #
                # Cashier explicitly approved a negotiated price.
                # --------------------------------------------------

                else:

                    if submitted_price is None:
                        raise Exception(
                            f"Selling price is required for " f"{variant.sku}."
                        )

                    try:

                        actual_selling_price = Decimal(str(submitted_price))

                    except (InvalidOperation, ValueError, TypeError):
                        raise Exception(f"Invalid selling price for " f"{variant.sku}.")

                    if actual_selling_price <= 0:
                        raise Exception(
                            f"Selling price for {variant.sku} "
                            f"must be greater than zero."
                        )

                # ==================================================
                # BUYING PRICE
                # ==================================================

                buying_price = (
                    Decimal(str(selected_imei_obj.buying_price))
                    if selected_imei_obj is not None and selected_imei_obj.buying_price is not None
                    else Decimal(str(variant.buying_price))
                )

                # ==================================================
                # LINE TOTAL
                # ==================================================

                line_total = actual_selling_price * quantity

                # ==================================================
                # LINE PROFIT
                # ==================================================

                line_profit = (actual_selling_price - buying_price) * quantity

                # ==================================================
                # CREATE SALE ITEM
                # ==================================================

                sale_item = SaleItem(
                    product_variant_id=variant.id,
                    quantity=quantity,
                    buying_price=buying_price,
                    selling_price=actual_selling_price,
                    total=line_total,
                    profit=line_profit,
                )

                sale_item.sale = sale

                db.session.add(sale_item)

                # ==================================================
                # IMEI VALIDATION
                # ==================================================

                imei_id = item.get("imei_id")

                imei_count = IMEI.query.filter_by(product_variant_id=variant.id).count()

                # --------------------------------------------------
                # REQUIRE IMEI WHEN SETTING IS ENABLED
                # --------------------------------------------------

                if (
                    settings.require_imei_when_available
                    and imei_count > 0
                    and not imei_id
                ):
                    raise Exception(f"Please select an IMEI for " f"{variant.sku}.")

                # --------------------------------------------------
                # VALIDATE SELECTED IMEI
                # --------------------------------------------------

                if imei_id:

                    imei = selected_imei_obj

                    # ------------------------------------------------
                    # ONE IMEI = ONE PHYSICAL DEVICE
                    # ------------------------------------------------

                    if quantity != 1:
                        raise Exception(
                            "IMEI tracked products can only " "be sold one at a time."
                        )

                    # ------------------------------------------------
                    # MARK DEVICE AS SOLD
                    # ------------------------------------------------

                    imei.status = "Sold"

                    # ------------------------------------------------
                    # ATTACH IMEI TO SALE ITEM
                    # ------------------------------------------------

                    sale_item.imei = imei

                # ==================================================
                # REDUCE STOCK
                # ==================================================

                variant.quantity -= quantity

                # ==================================================
                # UPDATE SALE TOTALS
                # ==================================================

                total_amount += line_total
                total_profit += line_profit

            # ======================================================
            # FINAL SALE TOTALS
            # ======================================================

            sale.total_amount = total_amount
            sale.profit = total_profit

            # ======================================================
            # PAYMENT / CREDIT / INSTALLMENT
            # ======================================================
            paid = Decimal(str(amount_paid if amount_paid is not None else total_amount))

            if paid < 0 or paid > total_amount:
                raise Exception("Amount paid cannot be negative or exceed the sale total.")

            if payment_method in ("Credit", "Installment"):
                if not customer:
                    raise Exception("A registered customer is required for credit/installment sales.")
                if due_date is None:
                    raise Exception("A due date is required for credit/installment sales.")
            else:
                paid = total_amount

            sale.amount_paid = paid
            sale.balance_due = total_amount - paid
            sale.payment_status = "Paid" if sale.balance_due <= 0 else ("Partial" if paid > 0 else "Unpaid")

            if paid > 0:
                db.session.add(SalePayment(
                    sale=sale,
                    amount=paid,
                    payment_method=payment_method,
                    reference=payment_reference,
                    notes=payment_notes,
                    received_by=created_by,
                ))

            # ======================================================
            # SAVE EVERYTHING
            # ======================================================

            db.session.commit()

            return sale

        # ==========================================================
        # ROLLBACK IF ANYTHING FAILS
        # ==========================================================

        except Exception:

            db.session.rollback()

            raise
