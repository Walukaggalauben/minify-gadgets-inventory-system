import random
import string

from db import db
from models.imei import IMEI
from models.product_variant import ProductVariant


def generate_imei():
    """Generate a unique 15-digit IMEI."""

    while True:
        imei = ''.join(random.choices(string.digits, k=15))

        exists = IMEI.query.filter_by(imei=imei).first()

        if not exists:
            return imei


def generate_serial():
    """Generate a unique serial number."""

    while True:
        serial = "SN" + ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )

        exists = IMEI.query.filter_by(serial_number=serial).first()

        if not exists:
            return serial


def seed_imeis():

    variants = ProductVariant.query.all()

    total = 0

    for variant in variants:

        for _ in range(variant.quantity):

            db.session.add(
                IMEI(
                    product_variant_id=variant.id,
                    imei=generate_imei(),
                    serial_number=generate_serial(),
                    status="In Stock",
                    
                    notes="Demo IMEI"
                )
            )

            total += 1

    db.session.commit()

    print(f"✓ {total} IMEIs created.")