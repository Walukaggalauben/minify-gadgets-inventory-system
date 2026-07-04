from models.role import Role
from db import db


def seed_roles():

    roles = [

        {
            "name": "Super Administrator",
            "description": "Full system access"
        },

        {
            "name": "Administrator",
            "description": "Manages daily operations"
        },

        {
            "name": "Inventory Manager",
            "description": "Manages inventory"
        },

        {
            "name": "Sales Manager",
            "description": "Manages sales"
        },

        {
            "name": "Sales Person",
            "description": "Handles customer sales"
        },

        {
            "name": "Technician",
            "description": "Handles repairs"
        },

        {
            "name": "Accountant",
            "description": "Handles finance"
        }

    ]

    for item in roles:

        exists = Role.query.filter_by(
            name=item["name"]
        ).first()

        if not exists:

            role = Role(
                name=item["name"],
                description=item["description"]
            )

            db.session.add(role)

    db.session.commit()

    print("Roles seeded successfully.")