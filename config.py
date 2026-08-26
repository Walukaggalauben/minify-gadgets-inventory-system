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

    # =====================================
    # Password recovery / SMTP
    # =====================================

    PASSWORD_RESET_TOKEN_MAX_AGE = int(os.getenv("PASSWORD_RESET_TOKEN_MAX_AGE", "900"))
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes"}
