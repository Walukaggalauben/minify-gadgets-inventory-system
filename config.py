import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =====================================
    # Flask
    # =====================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Keep False for local HTTP development.
    # Change to True only when deployed behind HTTPS.
    SESSION_COOKIE_SECURE = False

    # =====================================
    # Database
    # =====================================

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('MYSQL_USER')}:"
        f"{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}/"
        f"{os.getenv('MYSQL_DB')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =====================================
    # MySQL Backup / Restore
    # =====================================

    MYSQLDUMP_PATH = os.getenv("MYSQLDUMP_PATH")
    MYSQL_PATH = os.getenv("MYSQL_PATH")

    # =====================================
    # Uploads
    # =====================================

    UPLOAD_FOLDER = "uploads"

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # =====================================
    # Application
    # =====================================

    APP_NAME = "MINIFY GADGETS ERP V2"
