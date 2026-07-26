from app import app

from seeders.role_seeder import seed_roles
from seeders.admin_seeder import seed_admin
from seeders.category_seeder import seed_categories
from seeders.brand_seeder import seed_brands
from seeders.product_seeder import seed_products
from seeders.variant_seeder import seed_variants
from seeders.imei_seeder import seed_imeis
from seeders.supplier_seeder import seed_suppliers
from .purchase_seeder import seed_purchases


with app.app_context():

    print("Seeding database...")

    seed_roles()

    seed_admin()
    
    seed_categories()
    
    seed_brands()
    
    seed_products()
    
    seed_variants()
    
    seed_suppliers()
    
    seed_purchases()
    
    seed_imeis()
    
   

    print("Finished.")