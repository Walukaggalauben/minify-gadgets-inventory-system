from flask import Flask, request, session, redirect, url_for
from flask_migrate import Migrate
import os

from config import Config
from db import db


def create_app():

    app = Flask(__name__)
    @app.template_filter("datetimeformat")
    def datetimeformat(value):
        from datetime import datetime

        try:
            return datetime.fromtimestamp(float(value)).strftime(
                "%d %b %Y, %I:%M %p"
            )
        except (TypeError, ValueError, OSError):
            return "-"

    app.config.from_object(Config)

    # Upload configuration
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # Import models
    from models.role import Role
    from models.user import User
    from models.category import Category
    from models.brand import Brand
    from models.product import Product
    from models.product_variant import ProductVariant
    from models.customer import Customer
    from models.imei import IMEI
    from models.supplier import Supplier
    from models.purchase import Purchase
    from models.purchase_item import PurchaseItem
    from models.sale import Sale
    from models.sale_item import SaleItem
    from models.trade_in_rule import TradeInRule
    from models.company import Company
    from models.system_setting import SystemSetting
    from models.expense import Expense
    from models.sale_payment import SalePayment

    # Make company available in every template
    @app.context_processor
    def inject_company():
        return {"company": Company.query.first()}

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.dashboard import dashboard_bp
    from routes.category import category_bp
    from routes.brand import brand_bp
    from routes.product import product_bp
    from routes.product_variant import variant_bp
    from routes.imei import imei_bp
    from routes.supplier import supplier_bp
    from routes.purchase import purchase_bp
    from routes.trade_in import trade_in_bp
    from routes.trade_in_rules import trade_in_rules_bp
    from routes.sale import sale_bp
    from routes.customer import customer_bp
    from routes.company import company_bp
    from routes.report import report_bp
    from routes.backup import backup_bp

    from routes.system_settings import system_settings_bp
    from routes.expenses import expenses_bp
    from routes.inventory import inventory_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(variant_bp)
    app.register_blueprint(imei_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(trade_in_bp)
    app.register_blueprint(trade_in_rules_bp)
    app.register_blueprint(sale_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(system_settings_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(inventory_bp)

    @app.before_request
    def enforce_session_auth():
        public_endpoints = {"auth.login", "static"}
        if request.endpoint in public_endpoints or request.path.startswith("/static/"):
            return None
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return None

    Migrate(app, db)

    with app.app_context():

        from services.trade_in_rule_service import TradeInRuleService

        TradeInRuleService.seed_defaults()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
