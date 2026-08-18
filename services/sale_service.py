from decimal import Decimal, InvalidOperation


from db import db

from models.sale import Sale
from models.sale_item import SaleItem
from models.sale_payment import SalePayment
from models.product_variant import ProductVariant
from models.imei import IMEI
from models.currency import Currency
from models.customer_credit import CustomerCredit

from services.currency_service import CurrencyService
from utils.timezone import application_now


class SaleService:

    # ==========================================================
    # INVOICE NUMBER
    # ==========================================================

    @staticmethod
    def generate_invoice_number():
        """
        Generate a unique invoice number.

        Example:
        INV-20260815-130245-123
        """

        return application_now().strftime("INV-%Y%m%d-%H%M%S-%f")[:-3]

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
        amount_paid=0,
        payment_currency="UGX",
        manual_exchange_rate=None,
        due_date=None,
        payment_reference=None,
        payment_notes=None,
    ):

        try:

            # ==================================================
            # VALIDATE CART
            # ==================================================

            if not items:
                raise Exception("Sale must contain at least one item.")

            # ==================================================
            # CUSTOMER
            # ==================================================

            # Check whether the system requires a customer
            # to be selected for every sale.
            from models.system_setting import SystemSetting

            settings = SystemSetting.get_settings()

            require_customer = getattr(
                settings,
                "require_customer_on_sale",
                False,
            )

            if require_customer and not customer_id:
                raise Exception("A customer is required for this sale.")

            customer = None

            if customer_id:
                try:
                    customer_id = int(customer_id)
                except (ValueError, TypeError):
                    raise Exception("Invalid customer selected.")

                from models.customer import Customer

                customer = Customer.query.get(customer_id)

                if not customer:
                    raise Exception("Selected customer was not found.")

                customer_name = customer.full_name
                customer_phone = customer.phone

            # ==================================================
            # NORMALIZE PAYMENT CURRENCY
            # ==================================================

            payment_currency = str(payment_currency or "UGX").strip().upper()

            currency = Currency.query.filter_by(code=payment_currency).first()

            if not currency:
                raise Exception(f"Currency '{payment_currency}' was not found.")

            # ==================================================
            # CREATE SALE
            # ==================================================
            #
            # IMPORTANT:
            # invoice_number MUST be generated here.
            #
            # ==================================================

            sale = Sale(
                invoice_number=SaleService.generate_invoice_number(),
                customer_id=customer.id if customer else None,
                customer_name=customer_name,
                customer_phone=customer_phone,
                payment_method=payment_method,
                created_by=created_by,
                sale_date=application_now().replace(tzinfo=None),
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
            # PROCESS SALE ITEMS
            # ==================================================

            for item in items:

                # --------------------------------------------------
                # PRODUCT VARIANT
                # --------------------------------------------------

                variant_id = item.get("variant_id")

                if not variant_id:
                    raise Exception("Sale item is missing a product variant.")

                try:
                    variant_id = int(variant_id)
                except (ValueError, TypeError):
                    raise Exception("Invalid product variant.")

                variant = (
                    ProductVariant.query.filter_by(id=variant_id)
                    .with_for_update()
                    .first()
                )

                if not variant:
                    raise Exception(f"Product variant {variant_id} " "was not found.")

                # --------------------------------------------------
                # QUANTITY
                # --------------------------------------------------

                try:
                    quantity = int(item.get("quantity", 0))
                except (ValueError, TypeError):
                    raise Exception(f"Invalid quantity for {variant.sku}.")

                if quantity <= 0:
                    raise Exception(
                        f"Quantity must be greater than zero " f"for {variant.sku}."
                    )

                # --------------------------------------------------
                # STOCK
                # --------------------------------------------------

                if variant.quantity < quantity:
                    raise Exception(
                        f"Insufficient stock for {variant.sku}. "
                        f"Only {variant.quantity} item(s) available."
                    )

                # ==================================================
                # SELLING PRICE
                # ==================================================

                standard_price = Decimal(str(variant.selling_price or 0))

                # --------------------------------------------------
                # IMEI
                # --------------------------------------------------

                selected_imei_id = item.get("imei_id")
                selected_imei_obj = None

                if selected_imei_id:

                    try:
                        selected_imei_id = int(selected_imei_id)
                    except (ValueError, TypeError):
                        raise Exception("Invalid IMEI selected.")

                    selected_imei_obj = (
                        IMEI.query.filter_by(id=selected_imei_id)
                        .with_for_update()
                        .first()
                    )

                    if not selected_imei_obj:
                        raise Exception("Selected IMEI was not found.")

                    if selected_imei_obj.status != "In Stock":
                        raise Exception("Selected IMEI is not available.")

                    if selected_imei_obj.product_variant_id != variant.id:
                        raise Exception(
                            "Selected IMEI does not belong " "to the selected product."
                        )

                    if selected_imei_obj.default_selling_price is not None:
                        standard_price = Decimal(
                            str(selected_imei_obj.default_selling_price)
                        )

                # ==================================================
                # PRICE OVERRIDE
                # ==================================================

                submitted_price = item.get("price")

                price_override_requested = bool(item.get("price_override", False))

                allow_price_override = getattr(
                    settings,
                    "allow_price_override",
                    False,
                )

                if price_override_requested and not allow_price_override:
                    raise Exception(
                        "Price override is not allowed " "by system settings."
                    )

                if not price_override_requested:

                    actual_selling_price = standard_price

                else:

                    if submitted_price is None:
                        raise Exception(
                            f"Selling price is required " f"for {variant.sku}."
                        )

                    try:
                        actual_selling_price = Decimal(str(submitted_price))
                    except (
                        InvalidOperation,
                        ValueError,
                        TypeError,
                    ):
                        raise Exception(f"Invalid selling price " f"for {variant.sku}.")

                    if actual_selling_price <= 0:
                        raise Exception(
                            f"Selling price for {variant.sku} "
                            "must be greater than zero."
                        )

                # ==================================================
                # BUYING PRICE
                # ==================================================

                if (
                    selected_imei_obj is not None
                    and selected_imei_obj.buying_price is not None
                ):
                    buying_price = Decimal(str(selected_imei_obj.buying_price))

                else:
                    buying_price = Decimal(str(variant.buying_price or 0))

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
                    sale=sale,
                    product_variant_id=variant.id,
                    quantity=quantity,
                    buying_price=buying_price,
                    selling_price=actual_selling_price,
                    total=line_total,
                    profit=line_profit,
                )

                # Add immediately so relationship/autoflush is safe
                # before IMEI validation queries below.
                db.session.add(sale_item)

                # ==================================================
                # IMEI VALIDATION
                # ==================================================

                imei_id = item.get("imei_id")

                imei_count = IMEI.query.filter_by(product_variant_id=variant.id).count()

                # --------------------------------------------------
                # REQUIRE IMEI WHEN AVAILABLE
                # --------------------------------------------------

                # Read setting if the application provides it.
                # Default is True when the setting exists.
                try:
                    from models.system_setting import SystemSetting

                    settings = SystemSetting.get_settings()

                    require_imei = getattr(
                        settings,
                        "require_imei_when_available",
                        False,
                    )

                    prevent_negative_stock = getattr(
                        settings,
                        "prevent_negative_stock",
                        True,
                    )

                except Exception:
                    require_imei = False
                    prevent_negative_stock = True

                if require_imei and imei_count > 0 and not imei_id:
                    raise Exception(f"Please select an IMEI for " f"{variant.sku}.")

                # --------------------------------------------------
                # SELECTED IMEI
                # --------------------------------------------------

                if imei_id:

                    imei = selected_imei_obj

                    if quantity != 1:
                        raise Exception(
                            "IMEI tracked products can only " "be sold one at a time."
                        )

                    imei.status = "Sold"

                    sale_item.imei = imei

                # ==================================================
                # REDUCE STOCK
                # ==================================================

                if prevent_negative_stock:
                    if variant.quantity < quantity:
                        raise Exception(f"Insufficient stock for " f"{variant.sku}.")

                variant.quantity -= quantity

                # ==================================================
                # TOTALS
                # ==================================================

                total_amount += line_total
                total_profit += line_profit

            # ======================================================
            # FINAL SALE TOTALS
            # ======================================================

            sale.total_amount = total_amount
            sale.profit = total_profit

            # ======================================================
            # PAYMENT
            # ======================================================

            try:
                paid = Decimal(str(amount_paid if amount_paid is not None else 0))
            except (
                InvalidOperation,
                ValueError,
                TypeError,
            ):
                raise Exception("Invalid amount paid.")

            if paid < 0:
                raise Exception("Amount received cannot be negative.")

            # ======================================================
            # CREDIT / INSTALLMENT
            # ======================================================

            if payment_method in (
                "Credit",
                "Installment",
            ):
                if not customer:
                    raise Exception(
                        "A registered customer is required "
                        "for credit/installment sales."
                    )

                if due_date is None:
                    raise Exception(
                        "A due date is required for " "credit/installment sales."
                    )

            # ======================================================
            # CONVERT PAYMENT TO UGX
            # ======================================================

            base_amount = Decimal("0.00")
            exchange_rate = Decimal("1.00000000")

            if paid > 0:
                if payment_currency == "UGX":
                    base_amount = paid
                else:
                    # Use the cashier/admin override when supplied;
                    # otherwise use the current live rate.
                    if manual_exchange_rate not in (None, "", 0):
                        try:
                            exchange_rate = Decimal(str(manual_exchange_rate))
                        except (InvalidOperation, ValueError, TypeError):
                            raise Exception("Invalid manual exchange rate.")

                        if exchange_rate <= 0:
                            raise Exception(
                                "Manual exchange rate must be greater than zero."
                            )

                        base_amount = paid * exchange_rate
                    else:
                        conversion = CurrencyService.convert_currency(
                            paid,
                            payment_currency,
                            "UGX",
                        )

                        base_amount = Decimal(str(conversion["converted_amount"]))
                        exchange_rate = Decimal(str(conversion["rate"]))

            # ======================================================
            # SALE PAYMENT TOTALS
            # ======================================================

            sale.amount_paid = base_amount

            # Balance is never negative. Any excess is an
            # overpayment/customer credit, not profit.
            sale.balance_due = max(
                total_amount - base_amount,
                Decimal("0.00"),
            )

            if sale.balance_due <= 0 and base_amount > 0:
                sale.payment_status = "Paid"
            elif base_amount > 0:
                sale.payment_status = "Partial"
            else:
                sale.payment_status = "Unpaid"

            # ======================================================
            # SAVE PAYMENT RECORD
            # ======================================================

            if paid > 0:
                payment = SalePayment(
                    sale=sale,
                    amount=base_amount,
                    original_amount=paid,
                    currency_id=currency.id,
                    exchange_rate=exchange_rate,
                    payment_method=payment_method,
                    reference=payment_reference,
                    notes=payment_notes,
                    received_by=created_by,
                )

                db.session.add(payment)

            # ======================================================
            # CUSTOMER OVERPAYMENT LEDGER
            # ======================================================
            # The excess is customer money, not sale profit. Create the
            # liability in the same transaction as the sale so it can never
            # exist in Sale.amount_paid without a corresponding credit row.
            overpayment = max(
                base_amount - total_amount,
                Decimal("0.00"),
            )

            if overpayment > 0:
                db.session.add(
                    CustomerCredit(
                        customer_id=customer_id,
                        sale=sale,
                        original_amount=overpayment,
                        remaining_amount=overpayment,
                        status="Outstanding",
                    )
                )

            # ======================================================
            # SAVE EVERYTHING
            # ======================================================

            db.session.commit()

            return sale

        except Exception as e:
            db.session.rollback()
            raise e
    # ==========================================================
    # CANCEL SALE
    # ==========================================================

    @staticmethod
    def cancel_sale(sale_id):

        try:

            # ==================================================
            # FIND SALE
            # ==================================================

            sale = Sale.query.get(sale_id)

            if not sale:
                raise Exception("Sale not found.")

            # ==================================================
            # ALREADY CANCELLED
            # ==================================================

            if sale.status == "Cancelled":
                raise Exception("Sale is already cancelled.")

            # ==================================================
            # CUSTOMER CREDIT CHECK
            # ==================================================

            credit = CustomerCredit.query.filter_by(
                sale_id=sale.id
            ).first()

            if credit:
                remaining_credit = Decimal(
                    str(credit.remaining_amount or 0)
                )

                if remaining_credit > 0:
                    raise Exception(
                        "This sale cannot be cancelled because "
                        f"UGX {remaining_credit:,.2f} of customer "
                        "credit is still outstanding."
                    )

            # ==================================================
            # RESTORE SALE ITEMS
            # ==================================================

            for sale_item in sale.items:

                variant = ProductVariant.query.get(
                    sale_item.product_variant_id
                )

                if not variant:
                    raise Exception(
                        "Product variant for sale item "
                        f"{sale_item.id} was not found."
                    )

                quantity = int(sale_item.quantity or 0)

                if quantity <= 0:
                    raise Exception(
                        f"Invalid quantity on sale item {sale_item.id}."
                    )

                # Restore inventory quantity.
                variant.quantity += quantity

                # ==================================================
                # RESTORE IMEI
                # ==================================================

                if sale_item.imei_id:

                    imei = IMEI.query.get(
                        sale_item.imei_id
                    )

                    if not imei:
                        raise Exception(
                            f"IMEI record {sale_item.imei_id} was not found."
                        )

                    if imei.status != "Sold":
                        raise Exception(
                            f"IMEI {imei.imei} cannot be restored because "
                            f"its current status is '{imei.status}'."
                        )

                    imei.status = "In Stock"

            # ==================================================
            # MARK SALE CANCELLED
            # ==================================================

            sale.status = "Cancelled"

            # ==================================================
            # SAVE EVERYTHING
            # ==================================================

            db.session.commit()

            return sale

        except Exception as e:
            db.session.rollback()
            raise e
