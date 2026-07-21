from models.user import User
from models.role import Role
from db import db


def seed_admin():

    # Check if administrator already exists
    admin = User.query.filter_by(
        username="admin"
    ).first()

    if admin:
        print("Administrator already exists.")
        return

    # Find Super Administrator role
    role = Role.query.filter_by(
        name="Super Administrator"
    ).first()

    if not role:
        print("Super Administrator role not found.")
        return

    admin = User(

        full_name="System Administrator",

        username="admin",

        email="admin@minifygadgets.com",

        phone="0700000000",

        role_id=role.id

    )

    admin.set_password("admin123")

    db.session.add(admin)

    db.session.commit()

    print("Administrator created successfully.")