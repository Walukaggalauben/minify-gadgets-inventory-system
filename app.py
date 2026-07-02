from flask import Flask

from config import Config
from db import db


def create_app():

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize Database
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)