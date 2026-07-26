from db import db
from models.product import Product
from models.brand import Brand
from models.category import Category


def seed_products():
    products = [
        # Apple
        ("Apple", "Smartphones", "iPhone 15"),
        ("Apple", "Smartphones", "iPhone 15 Plus"),
        ("Apple", "Smartphones", "iPhone 15 Pro"),
        ("Apple", "Smartphones", "iPhone 15 Pro Max"),
        ("Apple", "Smartphones", "iPhone 16"),
        ("Apple", "Smartphones", "iPhone 16 Plus"),
        ("Apple", "Smartphones", "iPhone 16 Pro"),
        ("Apple", "Smartphones", "iPhone 16 Pro Max"),

        # Samsung
        ("Samsung", "Smartphones", "Galaxy S24"),
        ("Samsung", "Smartphones", "Galaxy S24+"),
        ("Samsung", "Smartphones", "Galaxy S24 Ultra"),
        ("Samsung", "Smartphones", "Galaxy Z Fold 6"),
        ("Samsung", "Smartphones", "Galaxy Z Flip 6"),

        # Google
        ("Google", "Smartphones", "Pixel 9"),
        ("Google", "Smartphones", "Pixel 9 Pro"),
        ("Google", "Smartphones", "Pixel 9 Pro XL"),

        # Tecno
        ("Tecno", "Smartphones", "Camon 30"),
        ("Tecno", "Smartphones", "Camon 30 Premier"),
        ("Tecno", "Smartphones", "Spark 20"),

        # Infinix
        ("Infinix", "Smartphones", "Note 40 Pro"),
        ("Infinix", "Smartphones", "Zero 40"),
        ("Infinix", "Smartphones", "Hot 50"),

        # Xiaomi
        ("Xiaomi", "Smartphones", "Redmi Note 14 Pro"),
        ("Xiaomi", "Smartphones", "Redmi Note 14 Pro+"),
        ("Xiaomi", "Smartphones", "Xiaomi 14 Ultra"),

        # HP
        ("HP", "Laptops", "EliteBook 840 G10"),
        ("HP", "Laptops", "ProBook 450 G10"),

        # Dell
        ("Dell", "Laptops", "Latitude 7440"),
        ("Dell", "Laptops", "Inspiron 15"),

        # Lenovo
        ("Lenovo", "Laptops", "ThinkPad X1 Carbon"),
        ("Lenovo", "Laptops", "IdeaPad 5"),

        # Accessories
        ("Apple", "Accessories", "AirPods Pro 2"),
        ("Samsung", "Accessories", "Galaxy Buds 3"),
        ("JBL", "Audio Devices", "JBL Flip 6")
    ]

    added = 0

    for brand_name, category_name, product_name in products:

        brand = Brand.query.filter_by(name=brand_name).first()
        category = Category.query.filter_by(name=category_name).first()

        if not brand or not category:
            continue

        exists = Product.query.filter_by(
            name=product_name,
            brand_id=brand.id
        ).first()

        if exists:
            continue

        db.session.add(
            Product(
                name=product_name,
                category_id=category.id,
                brand_id=brand.id,
                description=f"{product_name} by {brand_name}",
                is_active=True
            )
        )

        added += 1

    db.session.commit()

    print(f"✅ {added} Products Seeded")