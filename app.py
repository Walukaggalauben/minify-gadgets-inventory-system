from flask import Flask
from flask_migrate import Migrate

from config import Config
from db import db


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # Import models
    from models.role import Role
    from models.user import User
    from models.category import Category
    from models.brand import Brand
    from models.product import Product
    from models.product_variant import ProductVariant
    from models.supplier import Supplier
    from models.purchase import Purchase
    from models.purchase_item import PurchaseItem
    from models.sale import Sale
    from models.sale_item import SaleItem
    from models.company import Company

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.category import category_bp
    from routes.brand import brand_bp
    from routes.product import product_bp
    from routes.product_variant import variant_bp
    from routes.imei import imei_bp
    from routes.supplier import supplier_bp
    from routes.purchase import purchase_bp
    from routes.sale import sale_bp
    from routes.company import company_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(variant_bp)
    app.register_blueprint(imei_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(sale_bp)
    app.register_blueprint(company_bp)
    

    Migrate(app, db)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)