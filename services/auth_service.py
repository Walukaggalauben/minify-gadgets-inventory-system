import re

from sqlalchemy import or_, func

from models.user import User


class AuthService:

    @staticmethod
    def _normalize_phone(value):
        if not value:
            return ""
        return re.sub(r"[\s\-()]", "", value.strip())

    @staticmethod
    def authenticate(identifier, password):

        identifier = (identifier or "").strip()

        if not identifier or not password:
            return None

        phone_identifier = AuthService._normalize_phone(identifier)
        text_identifier = identifier.lower()

        user = User.query.filter(
            User.is_active.is_(True),
            or_(
                func.lower(User.username) == text_identifier,
                func.lower(User.email) == text_identifier,
                User.phone == identifier,
                User.phone == phone_identifier,
            ),
        ).first()

        if not user:
            return None

        if not user.check_password(password):
            return None

        return user
