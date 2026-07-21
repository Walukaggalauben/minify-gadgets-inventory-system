from app import app
from db import db
from models.role import Role
from models.user import User

with app.app_context():

    # Check if admin already exists
    admin = User.query.filter_by(username="admin").first()

    if admin:
        print("Administrator already exists.")
        exit()

    # Get Super Administrator role
    role = Role.query.filter_by(name="Super Administrator").first()

    if not role:
        print("Super Administrator role not found.")
        exit()

    admin = User(
        full_name="System Administrator",
        username="admin",
        email="admin@minifygadgets.com",
        phone="0700000000",
        role_id=role.id,
        is_active=True
    )

    admin.set_password("admin123")

    db.session.add(admin)
    db.session.commit()

    print("Administrator created successfully!")