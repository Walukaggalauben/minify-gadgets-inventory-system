from decimal import Decimal
from datetime import datetime

from db import db

from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.product_variant import ProductVariant
from models.imei import IMEI
from models.system_setting import SystemSetting


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

                # Non-IMEI stock may be received by quantity. If IMEIs are supplied,
                # exactly one must be supplied for each physical unit.
                if imeis and len(imeis) != quantity:
                    raise Exception(
                        f"{variant.product.name}: Quantity and IMEI count do not match."
                    )

                if quantity <= 0:
                    raise Exception(f"Quantity for {variant.sku} must be greater than zero.")

                if buying_price < 0 or selling_price < 0:
                    raise Exception("Purchase prices cannot be negative.")

                if not imeis and quantity > 0:
                    # Valid non-IMEI stock; no unit records are created.
                    pass

                if SystemSetting.get_settings().auto_update_buying_price:
                    variant.buying_price = buying_price
                    variant.selling_price = selling_price

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


    # ============================================================
    # UPDATE PURCHASE
    # ============================================================

    @staticmethod
    def update_purchase(
        purchase,
        supplier_id,
        purchase_date,
        invoice_number,
        payment_method,
        notes,
        items,
    ):

        try:

            # ----------------------------------------------------
            # Do not edit cancelled purchases
            # ----------------------------------------------------

            if purchase.status == "Cancelled":
                raise Exception(
                    "A cancelled purchase cannot be edited."
                )

            # ----------------------------------------------------
            # Validate that at least one item exists
            # ----------------------------------------------------

            if not items:
                raise Exception(
                    "A purchase must contain at least one item."
                )

            # ----------------------------------------------------
            # For safety, only allow editing Received purchases
            # ----------------------------------------------------

            if purchase.status != "Received":
                raise Exception(
                    f"Purchase cannot be edited while its status is "
                    f"'{purchase.status}'."
                )

            # ----------------------------------------------------
            # Build a map of the OLD purchase quantities
            # ----------------------------------------------------

            old_items = {}

            for old_item in purchase.items:

                key = old_item.product_variant_id

                if key in old_items:
                    old_items[key]["quantity"] += old_item.quantity
                    old_items[key]["items"].append(old_item)

                else:
                    old_items[key] = {
                        "quantity": old_item.quantity,
                        "items": [old_item],
                    }

            # ----------------------------------------------------
            # Build a map of the NEW quantities
            # ----------------------------------------------------

            new_items = {}

            for item in items:

                variant_id = int(item["product_variant_id"])
                quantity = int(item["quantity"])

                if quantity <= 0:
                    raise Exception(
                        "Purchase quantities must be greater than zero."
                    )

                buying_price = Decimal(
                    str(item["unit_cost"])
                )

                selling_price = Decimal(
                    str(
                        item.get(
                            "default_selling_price",
                            0
                        )
                    )
                )

                if buying_price < 0 or selling_price < 0:
                    raise Exception(
                        "Purchase prices cannot be negative."
                    )

                if variant_id in new_items:

                    new_items[variant_id]["quantity"] += quantity

                else:

                    new_items[variant_id] = {
                        "quantity": quantity,
                        "unit_cost": buying_price,
                        "selling_price": selling_price,
                    }

            # ----------------------------------------------------
            # Calculate inventory changes
            # ----------------------------------------------------

            all_variant_ids = set(
                old_items.keys()
            ) | set(
                new_items.keys()
            )

            for variant_id in all_variant_ids:

                variant = ProductVariant.query.get(
                    variant_id
                )

                if not variant:
                    raise Exception(
                        f"Product Variant {variant_id} not found."
                    )

                old_quantity = old_items.get(
                    variant_id,
                    {}
                ).get(
                    "quantity",
                    0
                )

                new_quantity = new_items.get(
                    variant_id,
                    {}
                ).get(
                    "quantity",
                    0
                )

                difference = (
                    new_quantity - old_quantity
                )

                # ------------------------------------------------
                # Quantity decreased
                # ------------------------------------------------

                if difference < 0:

                    decrease = abs(difference)

                    if variant.quantity < decrease:

                        raise Exception(
                            f"Cannot reduce the purchase quantity for "
                            f"{variant.product.name} ({variant.sku}). "
                            f"Only {variant.quantity} units are currently "
                            f"available in stock."
                        )

                # ------------------------------------------------
                # Apply inventory difference
                # ------------------------------------------------

                variant.quantity += difference

                # ------------------------------------------------
                # Update prices when this variant still exists
                # ------------------------------------------------

                if variant_id in new_items:

                    variant.buying_price = new_items[
                        variant_id
                    ]["unit_cost"]

                    variant.selling_price = new_items[
                        variant_id
                    ]["selling_price"]

            # ----------------------------------------------------
            # Remove old purchase items
            # ----------------------------------------------------

            for old_item in list(purchase.items):

                db.session.delete(old_item)

            db.session.flush()

            # ----------------------------------------------------
            # Create new purchase items
            # ----------------------------------------------------

            grand_total = Decimal("0.00")

            for item in items:

                variant = ProductVariant.query.get(
                    int(item["product_variant_id"])
                )

                quantity = int(
                    item["quantity"]
                )

                buying_price = Decimal(
                    str(item["unit_cost"])
                )

                subtotal = (
                    buying_price * quantity
                )

                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_variant_id=variant.id,
                    quantity=quantity,
                    unit_cost=buying_price,
                    subtotal=subtotal,
                )

                db.session.add(
                    purchase_item
                )

                grand_total += subtotal

            # ----------------------------------------------------
            # Update purchase information
            # ----------------------------------------------------

            purchase.supplier_id = supplier_id
            purchase.purchase_date = purchase_date
            purchase.invoice_number = invoice_number
            purchase.payment_method = payment_method
            purchase.notes = notes
            purchase.total_amount = grand_total

            db.session.commit()

            return purchase

        except Exception as e:

            db.session.rollback()

            raise e

    # ============================================================
    # CANCEL PURCHASE
    # ============================================================

    @staticmethod
    def cancel_purchase(purchase):

        try:

            # ----------------------------------------------------
            # Already cancelled
            # ----------------------------------------------------

            if purchase.status == "Cancelled":
                raise Exception("This purchase has already been cancelled.")

            # ----------------------------------------------------
            # Only received purchases affect inventory
            # ----------------------------------------------------

            if purchase.status != "Received":
                raise Exception(
                    f"Purchase cannot be cancelled because its status is "
                    f"'{purchase.status}'."
                )

            # ----------------------------------------------------
            # Check that enough stock still exists
            # ----------------------------------------------------

            for item in purchase.items:

                variant = ProductVariant.query.get(
                    item.product_variant_id
                )

                if not variant:
                    raise Exception(
                        f"Product Variant for purchase item {item.id} "
                        f"could not be found."
                    )

                if variant.quantity < item.quantity:
                    raise Exception(
                        f"Cannot cancel this purchase. "
                        f"{variant.product.name} ({variant.sku}) "
                        f"does not have enough remaining stock to reverse "
                        f"the purchased quantity of {item.quantity}."
                    )

            # ----------------------------------------------------
            # Reverse inventory
            # ----------------------------------------------------

            for item in purchase.items:

                variant = ProductVariant.query.get(
                    item.product_variant_id
                )

                variant.quantity -= item.quantity

            # ----------------------------------------------------
            # Mark purchase as cancelled
            # ----------------------------------------------------

            purchase.status = "Cancelled"

            db.session.commit()

            return purchase

        except Exception as e:

            db.session.rollback()

            raise e
