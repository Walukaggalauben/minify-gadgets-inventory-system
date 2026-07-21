from db import db
from models.brand import Brand


class BrandService:

    @staticmethod
    def get_all():
        return Brand.query.order_by(Brand.name).all()

    @staticmethod
    def get(brand_id):
        return Brand.query.get_or_404(brand_id)

    @staticmethod
    def create(data):
        brand = Brand(
            name=data["name"],
            logo=data.get("logo"),
            description=data.get("description"),
            is_active=True
        )

        db.session.add(brand)
        db.session.commit()

        return brand

    @staticmethod
    def update(brand, data):
        brand.name = data["name"]
        brand.logo = data.get("logo")
        brand.description = data.get("description")

        db.session.commit()

        return brand

    @staticmethod
    def toggle_status(brand):
        brand.is_active = not brand.is_active
        db.session.commit()