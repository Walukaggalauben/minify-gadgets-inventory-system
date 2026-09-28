from decimal import Decimal

from db import db
from models.imei import IMEI
from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.product_variant import ProductVariant
from utils.timezone import application_now


class IMEIService:

    @staticmethod
    def get_all():
        return IMEI.query.order_by(IMEI.created_at.desc()).all()

    @staticmethod
    def get(imei_id):
        return IMEI.query.get_or_404(imei_id)

    @staticmethod
    def receive_device(data, created_by):
        variant = ProductVariant.query.get(data["product_variant_id"])
        if not variant:
            raise ValueError("Product Variant not found.")
        imei_number = (data.get("imei") or "").strip()
        serial_number = (data.get("serial_number") or "").strip() or None
        if not imei_number:
            raise ValueError("IMEI is required.")
        if IMEI.query.filter_by(imei=imei_number).first():
            raise ValueError("IMEI already exists.")
        if serial_number and IMEI.query.filter_by(serial_number=serial_number).first():
            raise ValueError("Serial number already exists.")
        supplier_id = int(data["supplier_id"])
        buying_price = Decimal(str(data.get("buying_price") or "0"))
        selling_price = Decimal(str(data.get("selling_price") or "0"))
        last_purchase = Purchase.query.order_by(Purchase.id.desc()).first()
        last_number = 0
        if last_purchase:
            try:
                last_number = int(last_purchase.purchase_number.split("-")[-1])
            except Exception:
                last_number = 0
        purchase_number = f"PUR-{application_now().year}-{last_number + 1:06d}"
        purchase = Purchase(purchase_number=purchase_number, supplier_id=supplier_id, purchase_date=data["purchase_date"], invoice_number=(data.get("invoice_number") or "").strip() or None, payment_method=data.get("payment_method") or "Cash", notes=(data.get("notes") or "").strip() or "Individual device received through IMEI intake.", created_by=created_by, status="Received", total_amount=buying_price)
        db.session.add(purchase)
        db.session.flush()
        purchase_item = PurchaseItem(purchase_id=purchase.id, product_variant_id=variant.id, quantity=1, unit_cost=buying_price, subtotal=buying_price)
        db.session.add(purchase_item)
        db.session.flush()
        imei = IMEI(product_variant_id=variant.id, purchase_item_id=purchase_item.id, imei=imei_number, serial_number=serial_number, status="In Stock", buying_price=buying_price, default_selling_price=selling_price, acquisition_source="Purchase", received_date=application_now().replace(tzinfo=None), notes=(data.get("notes") or "").strip() or None)
        db.session.add(imei)
        variant.quantity += 1
        variant.buying_price = buying_price
        variant.selling_price = selling_price
        db.session.commit()
        return imei

    @staticmethod
    def create(data):

        # Check if IMEI already exists
        existing = IMEI.query.filter_by(
            imei=data["imei"]
        ).first()

        if existing:
            raise ValueError("IMEI already exists.")

        # Check if serial number already exists
        if data.get("serial_number"):
            existing_serial = IMEI.query.filter_by(
                serial_number=data["serial_number"]
            ).first()

            if existing_serial:
                raise ValueError("Serial number already exists.")

        imei = IMEI(
            product_variant_id=data["product_variant_id"],
            imei=data["imei"],
            serial_number=data.get("serial_number"),
            status=data.get("status", "In Stock"),
            notes=data.get("notes")
        )

        db.session.add(imei)
        db.session.commit()

        return imei

    @staticmethod
    def update(imei, data):

        # A sold/purchase-traceable IMEI is historical inventory data.
        # Its identity, variant and status must not be rewritten from the
        # generic IMEI editor. Notes remain editable.
        has_sale_history = bool(imei.sale_items)
        has_purchase_history = imei.purchase_item_id is not None

        requested_serial = (data.get("serial_number") or "").strip() or None

        if has_sale_history:
            requested_imei = str(data.get("imei", imei.imei)).strip()
            requested_variant = int(data["product_variant_id"]) if data.get("product_variant_id") else imei.product_variant_id
            requested_status = data.get("status", imei.status)

            if (
                requested_imei != imei.imei
                or requested_variant != imei.product_variant_id
                or requested_status != imei.status
            ):
                raise ValueError(
                    "This IMEI has sale history. Its IMEI, product variant, and status "
                    "cannot be changed, but the serial number and notes can be updated."
                )

        if has_purchase_history:
            requested_imei = str(data.get("imei", imei.imei)).strip()
            requested_variant = int(data["product_variant_id"]) if data.get("product_variant_id") else imei.product_variant_id

            if (
                requested_imei != imei.imei
                or requested_variant != imei.product_variant_id
            ):
                raise ValueError(
                    "This IMEI is linked to a purchase. Its IMEI and product variant "
                    "cannot be changed, but the serial number can be updated."
                )

        # Prevent duplicate IMEI
        existing = IMEI.query.filter(
            IMEI.imei == data["imei"],
            IMEI.id != imei.id
        ).first()

        if existing:
            raise ValueError("IMEI already exists.")

        # Prevent duplicate Serial Number
        if requested_serial:
            existing_serial = IMEI.query.filter(
                IMEI.serial_number == requested_serial,
                IMEI.id != imei.id
            ).first()

            if existing_serial:
                raise ValueError("Serial number already exists.")

        imei.product_variant_id = data["product_variant_id"]
        imei.imei = data["imei"]
        imei.serial_number = requested_serial
        imei.status = data.get("status", imei.status)
        imei.notes = data.get("notes")

        db.session.commit()

        return imei

    @staticmethod
    def delete(imei):

        if imei.purchase_item_id is not None or imei.sale_items:
            raise ValueError(
                "This IMEI is part of inventory/sales history and cannot be deleted."
            )

        db.session.delete(imei)
        db.session.commit()

    @staticmethod
    def search(keyword):

        return IMEI.query.filter(
            db.or_(
                IMEI.imei.contains(keyword),
                IMEI.serial_number.contains(keyword)
            )
        ).all()