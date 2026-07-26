from models.category import Category
from db import db


def seed_categories():
    categories = [
        "Smartphones",
        "Tablets",
        "Laptops",
        "Smart Watches",
        "Accessories",
        "Audio Devices",
        "Gaming",
        "Networking"
    ]

    added = 0

    for name in categories:
        exists = Category.query.filter_by(name=name).first()

        if not exists:
            db.session.add(Category(name=name))
            added += 1

    db.session.commit()

    print(f"✅ {added} Categories Seeded")