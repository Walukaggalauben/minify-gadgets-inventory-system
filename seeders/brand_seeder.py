from db import db
from models.brand import Brand


def seed_brands():
    brands = [
        {
            "name": "Apple",
            "description": "Apple Inc."
        },
        {
            "name": "Samsung",
            "description": "Samsung Electronics"
        },
        {
            "name": "Google",
            "description": "Google Pixel Devices"
        },
        {
            "name": "Xiaomi",
            "description": "Xiaomi Mobile"
        },
        {
            "name": "Tecno",
            "description": "Tecno Mobile"
        },
        {
            "name": "Infinix",
            "description": "Infinix Mobility"
        },
        {
            "name": "Oppo",
            "description": "OPPO Mobile"
        },
        {
            "name": "Vivo",
            "description": "Vivo Mobile"
        },
        {
            "name": "Nokia",
            "description": "Nokia Mobile"
        },
        {
            "name": "Huawei",
            "description": "Huawei Technologies"
        },
        {
            "name": "HP",
            "description": "HP Computers"
        },
        {
            "name": "Dell",
            "description": "Dell Technologies"
        },
        {
            "name": "Lenovo",
            "description": "Lenovo Computers"
        },
        {
            "name": "Asus",
            "description": "ASUS Computers"
        },
        {
            "name": "JBL",
            "description": "JBL Audio"
        }
    ]

    added = 0

    for item in brands:
        exists = Brand.query.filter_by(name=item["name"]).first()

        if not exists:
            db.session.add(
                Brand(
                    name=item["name"],
                    description=item["description"],
                    is_active=True
                )
            )
            added += 1

    db.session.commit()

    print(f"✅ {added} Brands Seeded")