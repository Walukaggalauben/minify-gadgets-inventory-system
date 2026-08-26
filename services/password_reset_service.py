from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from services.email_service import EmailService
from models.user import User


class PasswordResetService:
    SALT = "minify-gadgets-password-reset-v1"

    @staticmethod
    def _serializer():
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    @staticmethod
    def normalize_email(value):
        value = (value or "").strip().lower()
        return value or None

    @staticmethod
    def create_token(user):
        updated_at = user.updated_at.isoformat() if user.updated_at else ""
        return PasswordResetService._serializer().dumps(
            {
                "user_id": user.id,
                "email": user.email,
                "updated_at": updated_at,
            },
            salt=PasswordResetService.SALT,
        )

    @staticmethod
    def load_token(token, max_age=None):
        max_age = max_age or current_app.config.get("PASSWORD_RESET_TOKEN_MAX_AGE", 900)
        try:
            data = PasswordResetService._serializer().loads(
                token,
                salt=PasswordResetService.SALT,
                max_age=max_age,
            )
        except (BadSignature, SignatureExpired):
            return None

        user = User.query.get(data.get("user_id"))
        if not user or not user.is_active:
            return None

        email = PasswordResetService.normalize_email(user.email)
        if not email or email != PasswordResetService.normalize_email(data.get("email")):
            return None

        current_updated_at = user.updated_at.isoformat() if user.updated_at else ""
        if current_updated_at != data.get("updated_at", ""):
            return None

        return user

    @staticmethod
    def request_reset(email, reset_url_builder):
        email = PasswordResetService.normalize_email(email)
        if not email:
            return False

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user:
            return False

        token = PasswordResetService.create_token(user)
        reset_url = reset_url_builder(token)
        expires_minutes = max(1, int(current_app.config.get("PASSWORD_RESET_TOKEN_MAX_AGE", 900) / 60))
        return EmailService.send_password_reset(
            user.email,
            reset_url,
            expires_minutes,
        )

    @staticmethod
    def reset_password(user, new_password):
        if not new_password or len(new_password) < 8:
            return False, "Password must be at least 8 characters long."

        user.set_password(new_password)
        from db import db
        db.session.commit()
        return True, "Password reset successfully. You can now log in."
