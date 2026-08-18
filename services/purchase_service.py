from decimal import Decimal
from utils.timezone import application_now

from db import db

from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.product_variant import ProductVariant
from models.imei import IMEI
from models.system_setting import SystemSetting


class PurchaseService:

    @staticmethod
    def generate_purchase_number():
        year = application_now().year

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

            # ======================================================
            # PROCESS PURCHASE ITEMS
            # ======================================================

            for item in items:

                variant = ProductVariant.query.get(item["product_variant_id"])

                if not variant:
                    raise Exception("Product Variant not found.")

                quantity = int(item["quantity"])

                buying_price = Decimal(str(item["unit_cost"]))

                selling_price = Decimal(
                    str(
                        item.get(
                            "default_selling_price",
                            variant.selling_price,
                        )
                    )
                )

                imeis = item.get("imeis", [])

                # --------------------------------------------------
                # VALIDATE IMEI COUNT
                # --------------------------------------------------

                if imeis and len(imeis) != quantity:
                    raise Exception(
                        f"{variant.product.name}: "
                        f"Quantity and IMEI count do not match."
                    )

                if quantity <= 0:
                    raise Exception(
                        f"Quantity for {variant.sku} " f"must be greater than zero."
                    )

                if buying_price < 0 or selling_price < 0:
                    raise Exception("Purchase prices cannot be negative.")

                # --------------------------------------------------
                # UPDATE VARIANT PRICES
                # --------------------------------------------------

                if SystemSetting.get_settings().auto_update_buying_price:
                    variant.buying_price = buying_price
                    variant.selling_price = selling_price

                # --------------------------------------------------
                # CREATE PURCHASE ITEM
                # --------------------------------------------------

                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_variant_id=variant.id,
                    quantity=quantity,
                    unit_cost=buying_price,
                    subtotal=buying_price * quantity,
                )

                db.session.add(purchase_item)

                # We need the PurchaseItem ID before attaching
                # individual IMEIs.
                db.session.flush()

                # --------------------------------------------------
                # UPDATE CURRENT STOCK
                # --------------------------------------------------

                variant.quantity += quantity

                grand_total += buying_price * quantity

                # ==================================================
                # CREATE IMEIs
                # ==================================================

                for imei_number in imeis:

                    imei_number = imei_number.strip()

                    if not imei_number:
                        continue

                    # ------------------------------------------------
                    # DUPLICATE CHECK
                    # ------------------------------------------------

                    exists = IMEI.query.filter_by(imei=imei_number).first()

                    if exists:
                        raise Exception(f"IMEI already exists: {imei_number}")

                    # ------------------------------------------------
                    # CREATE IMEI WITH PURCHASE TRACE
                    # ------------------------------------------------

                    new_imei = IMEI(
                        product_variant_id=variant.id,
                        purchase_item_id=purchase_item.id,
                        imei=imei_number,
                        buying_price=buying_price,
                        default_selling_price=selling_price,
                        acquisition_source="Purchase",
                        received_date=application_now().replace(tzinfo=None),
                        status="In Stock",
                    )

                    db.session.add(new_imei)

            # ======================================================
            # FINALIZE PURCHASE
            # ======================================================

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
                raise Exception("A cancelled purchase cannot be edited.")

            # ----------------------------------------------------
            # Validate at least one item
            # ----------------------------------------------------

            if not items:
                raise Exception("A purchase must contain at least one item.")

            # ----------------------------------------------------
            # Only Received purchases may be edited
            # ----------------------------------------------------

            if purchase.status != "Received":
                raise Exception(
                    f"Purchase cannot be edited while its "
                    f"status is '{purchase.status}'."
                )

            # ====================================================
            # AUDIT PROTECTION
            # ====================================================
            #
            # Once an IMEI has been attached to a PurchaseItem,
            # that PurchaseItem becomes part of the permanent
            # acquisition history.
            #
            # It must never be deleted and recreated because doing
            # so would destroy the IMEI -> PurchaseItem -> Purchase
            # -> Supplier chain.
            # ====================================================

            old_items = list(purchase.items)

            old_by_variant = {}

            for old_item in old_items:

                variant_id = old_item.product_variant_id

                if variant_id in old_by_variant:
                    old_by_variant[variant_id]["items"].append(old_item)
                    old_by_variant[variant_id]["quantity"] += old_item.quantity
                else:
                    old_by_variant[variant_id] = {
                        "items": [old_item],
                        "quantity": old_item.quantity,
                    }

            # ----------------------------------------------------
            # Build new purchase quantities
            # ----------------------------------------------------

            new_items = {}

            for item in items:

                variant_id = int(item["product_variant_id"])

                quantity = int(item["quantity"])

                if quantity <= 0:
                    raise Exception("Purchase quantities must be greater than zero.")

                buying_price = Decimal(str(item["unit_cost"]))

                selling_price = Decimal(
                    str(
                        item.get(
                            "default_selling_price",
                            0,
                        )
                    )
                )

                if buying_price < 0 or selling_price < 0:
                    raise Exception("Purchase prices cannot be negative.")

                if variant_id in new_items:
                    new_items[variant_id]["quantity"] += quantity
                else:
                    new_items[variant_id] = {
                        "quantity": quantity,
                        "unit_cost": buying_price,
                        "selling_price": selling_price,
                    }

            # ====================================================
            # PROTECT IMEI-LINKED PURCHASE ITEMS
            # ====================================================

            for old_item in old_items:

                imei_count = IMEI.query.filter_by(purchase_item_id=old_item.id).count()

                if imei_count <= 0:
                    continue

                variant_id = old_item.product_variant_id

                new_entry = new_items.get(variant_id)

                if not new_entry:
                    raise Exception(
                        f"Purchase item {old_item.id} cannot be "
                        f"removed because {imei_count} IMEI(s) "
                        f"are linked to it. Preserve the item so "
                        f"purchase history remains auditable."
                    )

                if new_entry["quantity"] != old_item.quantity:
                    raise Exception(
                        f"Cannot change the quantity of "
                        f"{old_item.product_variant_id} on this "
                        f"purchase because {imei_count} IMEI(s) "
                        f"are linked to purchase item "
                        f"{old_item.id}."
                    )

            # ====================================================
            # CALCULATE INVENTORY DIFFERENCES
            # ====================================================

            all_variant_ids = set(old_by_variant.keys()) | set(new_items.keys())

            for variant_id in all_variant_ids:

                variant = ProductVariant.query.get(variant_id)

                if not variant:
                    raise Exception(f"Product Variant {variant_id} not found.")

                old_quantity = old_by_variant.get(
                    variant_id,
                    {},
                ).get("quantity", 0)

                new_quantity = new_items.get(
                    variant_id,
                    {},
                ).get("quantity", 0)

                difference = new_quantity - old_quantity

                # ------------------------------------------------
                # Quantity decreased
                # ------------------------------------------------

                if difference < 0:

                    decrease = abs(difference)

                    if variant.quantity < decrease:
                        raise Exception(
                            f"Cannot reduce the purchase "
                            f"quantity for "
                            f"{variant.product.name} "
                            f"({variant.sku}). "
                            f"Only {variant.quantity} "
                            f"units are currently available "
                            f"in stock."
                        )

                # ------------------------------------------------
                # Apply inventory difference
                # ------------------------------------------------

                variant.quantity += difference

                # ------------------------------------------------
                # Update variant prices
                # ------------------------------------------------

                if variant_id in new_items:

                    variant.buying_price = new_items[variant_id]["unit_cost"]

                    variant.selling_price = new_items[variant_id]["selling_price"]

            # ====================================================
            # RECONCILE PURCHASE ITEMS SAFELY
            # ====================================================
            #
            # IMPORTANT:
            # IMEI-linked items are updated in place.
            #
            # Items without IMEIs may still be removed and
            # recreated exactly as the previous workflow did.
            # ====================================================

            processed_old_ids = set()

            grand_total = Decimal("0.00")

            for variant_id, new_entry in new_items.items():

                matching_old_items = old_by_variant.get(
                    variant_id,
                    {},
                ).get("items", [])

                # ------------------------------------------------
                # Prefer an IMEI-linked item.
                # ------------------------------------------------

                linked_old_items = []

                for old_item in matching_old_items:

                    imei_count = IMEI.query.filter_by(
                        purchase_item_id=old_item.id
                    ).count()

                    if imei_count > 0:
                        linked_old_items.append(old_item)

                if linked_old_items:

                    if len(linked_old_items) > 1:
                        raise Exception(
                            f"Purchase contains multiple IMEI-linked "
                            f"items for product variant "
                            f"{variant_id}. "
                            f"Please resolve this purchase manually "
                            f"before editing it."
                        )

                    old_item = linked_old_items[0]

                    old_item.quantity = new_entry["quantity"]
                    old_item.unit_cost = new_entry["unit_cost"]
                    old_item.subtotal = new_entry["unit_cost"] * new_entry["quantity"]

                    # Keep linked physical IMEIs synchronized with the
                    # acquisition cost stored on this PurchaseItem.

                    linked_imeis = IMEI.query.filter_by(
                        purchase_item_id=old_item.id
                    ).all()

                    for imei in linked_imeis:
                        imei.buying_price = new_entry["unit_cost"]

                    grand_total += old_item.subtotal

                    continue

                # ------------------------------------------------
                # No IMEI-linked item.
                #
                # Reuse one existing item where possible.
                # ------------------------------------------------

                reusable_old = None

                for old_item in matching_old_items:

                    if old_item.id not in processed_old_ids:
                        reusable_old = old_item
                        break

                if reusable_old:

                    reusable_old.quantity = new_entry["quantity"]

                    reusable_old.unit_cost = new_entry["unit_cost"]

                    reusable_old.subtotal = (
                        new_entry["unit_cost"] * new_entry["quantity"]
                    )

                    processed_old_ids.add(reusable_old.id)

                    grand_total += reusable_old.subtotal

                else:

                    variant = ProductVariant.query.get(variant_id)

                    if not variant:
                        raise Exception(f"Product Variant {variant_id} " f"not found.")

                    purchase_item = PurchaseItem(
                        purchase_id=purchase.id,
                        product_variant_id=variant.id,
                        quantity=new_entry["quantity"],
                        unit_cost=new_entry["unit_cost"],
                        subtotal=(new_entry["unit_cost"] * new_entry["quantity"]),
                    )

                    db.session.add(purchase_item)

                    grand_total += purchase_item.subtotal

            # ====================================================
            # REMOVE ONLY SAFE OLD PURCHASE ITEMS
            # ====================================================

            for old_item in old_items:

                if old_item.id in processed_old_ids:
                    continue

                imei_count = IMEI.query.filter_by(purchase_item_id=old_item.id).count()

                if imei_count > 0:
                    raise Exception(
                        f"Purchase item {old_item.id} has "
                        f"{imei_count} linked IMEI(s) and cannot "
                        f"be deleted."
                    )

                db.session.delete(old_item)

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

            if purchase.status == "Cancelled":
                raise Exception("Purchase is already cancelled.")

            # ====================================================
            # IMEI AUDIT PROTECTION
            # ====================================================
            #
            # A purchase with physical IMEIs cannot be silently
            # cancelled because doing so would leave the physical
            # unit's acquisition history inconsistent.
            #
            # This is especially important for sold IMEIs because
            # their purchase cost is required for profit auditing.
            # ====================================================

            linked_imeis = []

            for item in purchase.items:

                item_imeis = IMEI.query.filter_by(purchase_item_id=item.id).all()

                linked_imeis.extend(item_imeis)

            if linked_imeis:

                sold_count = sum(1 for imei in linked_imeis if imei.status == "Sold")

                in_stock_count = sum(
                    1 for imei in linked_imeis if imei.status == "In Stock"
                )

                other_count = len(linked_imeis) - sold_count - in_stock_count

                details = (
                    f"{len(linked_imeis)} IMEI(s) are linked " f"to this purchase."
                )

                if sold_count:
                    details += f" {sold_count} are already Sold."

                if in_stock_count:
                    details += f" {in_stock_count} are still In Stock."

                if other_count:
                    details += f" {other_count} have another status."

                raise Exception(
                    "This purchase cannot be cancelled because "
                    "its physical IMEI history must be preserved. " + details
                )

            # ====================================================
            # PREVENT CANCELLATION IF STOCK CANNOT BE REVERSED
            # ====================================================

            for item in purchase.items:

                variant = ProductVariant.query.get(item.product_variant_id)

                if not variant:
                    raise Exception(
                        f"Product Variant " f"{item.product_variant_id} " f"not found."
                    )

                if variant.quantity < item.quantity:
                    raise Exception(
                        f"Cannot cancel purchase "
                        f"{purchase.purchase_number}. "
                        f"Insufficient current stock for "
                        f"{variant.product.name} "
                        f"({variant.sku})."
                    )

            # ====================================================
            # REVERSE INVENTORY
            # ====================================================

            for item in purchase.items:

                variant = ProductVariant.query.get(item.product_variant_id)

                variant.quantity -= item.quantity

            purchase.status = "Cancelled"

            db.session.commit()

            return purchase

        except Exception as e:
            db.session.rollback()
            raise e
