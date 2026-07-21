from models.user import User
from db import db


class AuthService:

    @staticmethod
    def authenticate(username, password):

        user = User.query.filter_by(
            username=username,
            is_active=True
        ).first()

        if not user:
            return None

        if not user.check_password(password):
            return None

        return user