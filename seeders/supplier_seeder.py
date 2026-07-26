from db import db
from models.supplier import Supplier


def seed_suppliers():

    suppliers = [

        {
            "name": "Apple Uganda Distributor",
            "contact_person": "Michael Kato",
            "phone": "0701001001",
            "email": "sales@appleug.co.ug",
            "address": "Kampala, Uganda"
        },

        {
            "name": "Samsung East Africa",
            "contact_person": "Grace Namusoke",
            "phone": "0701001002",
            "email": "sales@samsungea.com",
            "address": "Kampala, Uganda"
        },

        {
            "name": "Mobile Hub Kampala",
            "contact_person": "Brian Ssemanda",
            "phone": "0701001003",
            "email": "info@mobilehub.ug",
            "address": "Kampala Road"
        },

        {
            "name": "Tech Wholesale Ltd",
            "contact_person": "John Okello",
            "phone": "0701001004",
            "email": "orders@techwholesale.ug",
            "address": "Nakawa"
        },

        {
            "name": "Gadget World Supplies",
            "contact_person": "Sarah Achieng",
            "phone": "0701001005",
            "email": "sales@gadgetworld.ug",
            "address": "Ntinda"
        },

        {
            "name": "Digital Devices Uganda",
            "contact_person": "Peter Mugisha",
            "phone": "0701001006",
            "email": "contact@digitaldevices.ug",
            "address": "Bugolobi"
        },

        {
            "name": "Prime Electronics",
            "contact_person": "David Lule",
            "phone": "0701001007",
            "email": "info@primeelectronics.ug",
            "address": "Wandegeya"
        },

        {
            "name": "Global Phone Imports",
            "contact_person": "James Mutebi",
            "phone": "0701001008",
            "email": "sales@globalphones.ug",
            "address": "Kampala"
        }
    ]

    added = 0

    for item in suppliers:

        exists = Supplier.query.filter_by(
            name=item["name"]
        ).first()

        if exists:
            continue

        db.session.add(
            Supplier(
                name=item["name"],
                contact_person=item["contact_person"],
                phone=item["phone"],
                email=item["email"],
                address=item["address"],
                notes="Demo Supplier"
            )
        )

        added += 1

    db.session.commit()

    print(f"✅ {added} Suppliers Seeded")