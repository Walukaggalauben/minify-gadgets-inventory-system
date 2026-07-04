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

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Flask-Migrate
    Migrate(app, db)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)