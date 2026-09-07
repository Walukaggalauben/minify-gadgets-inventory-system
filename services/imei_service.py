from db import db
from models.imei import IMEI


class IMEIService:

    @staticmethod
    def get_all():
        return IMEI.query.order_by(IMEI.created_at.desc()).all()

    @staticmethod
    def get(imei_id):
        return IMEI.query.get_or_404(imei_id)

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