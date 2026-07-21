from db import db
from models.supplier import Supplier

try:
    from sqlalchemy import or_
except ImportError:
    or_ = db.or_


class SupplierService:

    @staticmethod
    def get_all():
        return Supplier.query.order_by(
            Supplier.name.asc()
        ).all()

    @staticmethod
    def get(supplier_id):
        return Supplier.query.get_or_404(supplier_id)

    @staticmethod
    def create(data):

        existing = Supplier.query.filter_by(
            name=data["name"]
        ).first()

        if existing:
            raise ValueError(
                "Supplier already exists."
            )

        supplier = Supplier(
            name=data["name"],
            contact_person=data.get("contact_person"),
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
            notes=data.get("notes")
        )

        db.session.add(supplier)
        db.session.commit()

        return supplier

    @staticmethod
    def update(supplier, data):

        existing = Supplier.query.filter(
            Supplier.name == data["name"],
            Supplier.id != supplier.id
        ).first()

        if existing:
            raise ValueError(
                "Supplier already exists."
            )

        supplier.name = data["name"]
        supplier.contact_person = data.get("contact_person")
        supplier.phone = data.get("phone")
        supplier.email = data.get("email")
        supplier.address = data.get("address")
        supplier.notes = data.get("notes")

        db.session.commit()

        return supplier

    @staticmethod
    def delete(supplier):

        db.session.delete(supplier)
        db.session.commit()

    @staticmethod
    def search(keyword):

        return Supplier.query.filter(
            or_(
                Supplier.name.contains(keyword),
                Supplier.contact_person.contains(keyword),
                Supplier.phone.contains(keyword),
                Supplier.email.contains(keyword)
            )
        ).order_by(
            Supplier.name.asc()
        ).all()