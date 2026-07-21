from app import app

from seeders.role_seeder import seed_roles
from seeders.admin_seeder import seed_admin


with app.app_context():

    print("Seeding database...")

    seed_roles()

    seed_admin()

    print("Finished.")