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

        # Prevent duplicate IMEI
        existing = IMEI.query.filter(
            IMEI.imei == data["imei"],
            IMEI.id != imei.id
        ).first()

        if existing:
            raise ValueError("IMEI already exists.")

        # Prevent duplicate Serial Number
        if data.get("serial_number"):
            existing_serial = IMEI.query.filter(
                IMEI.serial_number == data["serial_number"],
                IMEI.id != imei.id
            ).first()

            if existing_serial:
                raise ValueError("Serial number already exists.")

        imei.product_variant_id = data["product_variant_id"]
        imei.imei = data["imei"]
        imei.serial_number = data.get("serial_number")
        imei.status = data.get("status", imei.status)
        imei.notes = data.get("notes")

        db.session.commit()

        return imei

    @staticmethod
    def delete(imei):

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