import random

from db import db
from models.product import Product
from models.product_variant import ProductVariant


COLOURS = [
    "Black",
    "White",
    "Blue",
    "Silver",
    "Green",
    "Purple",
    "Gold"
]

VARIANTS = [
    ("128GB", "8GB"),
    ("256GB", "8GB"),
    ("256GB", "12GB"),
    ("512GB", "12GB"),
]


def seed_variants():

    added = 0

    for product in Product.query.all():

        for storage, ram in VARIANTS:

            colour = random.choice(COLOURS)

            sku = (
                product.name.replace(" ", "")
                + "-"
                + storage.replace("GB", "")
                + "-"
                + ram.replace("GB", "")
                + "-"
                + colour.upper()
            )

            exists = ProductVariant.query.filter_by(sku=sku).first()

            if exists:
                continue

            # ---------- Pricing ----------

            if "iPhone" in product.name:
                buying = random.randint(3000000, 6500000)
                selling = buying + random.randint(300000, 700000)

            elif "Galaxy" in product.name:
                buying = random.randint(2500000, 6000000)
                selling = buying + random.randint(300000, 700000)

            elif "Pixel" in product.name:
                buying = random.randint(2200000, 4500000)
                selling = buying + random.randint(250000, 600000)

            elif "EliteBook" in product.name or "Latitude" in product.name:
                buying = random.randint(1800000, 4000000)
                selling = buying + random.randint(250000, 600000)

            else:
                buying = random.randint(500000, 1800000)
                selling = buying + random.randint(100000, 400000)

            barcode = str(random.randint(100000000000, 999999999999))

            variant = ProductVariant(

                product_id=product.id,

                sku=sku,

                barcode=barcode,

                storage=storage,

                ram=ram,

                colour=colour,

                condition="Brand New",

                buying_price=buying,

                selling_price=selling,

                quantity=0,

                minimum_stock=2,

                warranty_months=12,

                is_active=True
            )

            db.session.add(variant)

            added += 1

    db.session.commit()

    print(f"✅ {added} Product Variants Seeded")