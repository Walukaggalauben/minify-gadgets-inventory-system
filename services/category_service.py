from db import db
from models.category import Category


class CategoryService:

    @staticmethod
    def get_all():
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def get(category_id):
        return Category.query.get_or_404(category_id)

    @staticmethod
    def create(data):
        category = Category(
            name=data["name"],
            description=data.get("description"),
            is_active=True
        )

        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def update(category, data):
        category.name = data["name"]
        category.description = data.get("description")

        db.session.commit()

        return category

    @staticmethod
    def toggle_status(category):
        category.is_active = not category.is_active
        db.session.commit()