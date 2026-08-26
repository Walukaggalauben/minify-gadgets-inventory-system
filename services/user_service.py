from sqlalchemy import or_, func
import re

from db import db
from models.user import User
from models.role import Role


class UserService:

    # ==========================================
    # NORMALIZATION HELPERS
    # ==========================================

    @staticmethod
    def normalize_username(value):
        return (value or "").strip()

    @staticmethod
    def normalize_email(value):
        value = (value or "").strip()
        return value.lower() if value else None

    @staticmethod
    def normalize_phone(value):
        if not value:
            return None
        value = re.sub(r"[\s\-()]", "", value.strip())
        return value or None

    # ==========================================
    # DASHBOARD STATISTICS
    # ==========================================

    @staticmethod
    def get_statistics():

        return {
            "total_users": User.query.count(),
            "active_users": User.query.filter_by(is_active=True).count(),
            "inactive_users": User.query.filter_by(is_active=False).count(),
            "administrators": User.query.join(Role)
            .filter(Role.name.ilike("%admin%"))
            .count(),
        }

    # ==========================================
    # USERS LIST
    # ==========================================

    @staticmethod
    def get_users(
        page=1,
        per_page=10,
        search="",
        role="",
        status=""
    ):

        query = User.query.join(Role)

        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%"),
                )
            )

        if role:
            query = query.filter(User.role_id == int(role))

        if status == "active":
            query = query.filter(User.is_active.is_(True))

        elif status == "inactive":
            query = query.filter(User.is_active.is_(False))

        pagination = query.order_by(
            User.full_name.asc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        return pagination

    # ==========================================
    # GET SINGLE USER
    # ==========================================

    @staticmethod
    def get_user(user_id):
        return User.query.get_or_404(user_id)

    # ==========================================
    # ROLES
    # ==========================================

    @staticmethod
    def get_all_roles():

        return (
            Role.query.filter_by(is_active=True)
            .order_by(Role.name.asc())
            .all()
        )

    # ==========================================
    # CHECK DUPLICATES
    # ==========================================

    @staticmethod
    def username_exists(username, exclude_id=None):

        username = UserService.normalize_username(username)

        query = User.query.filter(
            func.lower(User.username) == username.lower()
        )

        if exclude_id:
            query = query.filter(User.id != exclude_id)

        return query.first() is not None

    @staticmethod
    def email_exists(email, exclude_id=None):

        email = UserService.normalize_email(email)

        if not email:
            return False

        query = User.query.filter(
            func.lower(User.email) == email.lower()
        )

        if exclude_id:
            query = query.filter(User.id != exclude_id)

        return query.first() is not None

    @staticmethod
    def phone_exists(phone, exclude_id=None):

        phone = UserService.normalize_phone(phone)

        if not phone:
            return False

        query = User.query.filter(
            User.phone == phone
        )

        if exclude_id:
            query = query.filter(User.id != exclude_id)

        return query.first() is not None

    # ==========================================
    # CREATE USER
    # ==========================================

    @staticmethod
    def create_user(form):

        full_name = (form.get("full_name") or "").strip()
        username = UserService.normalize_username(form.get("username"))
        email = UserService.normalize_email(form.get("email"))
        phone = UserService.normalize_phone(form.get("phone"))
        password = form.get("password") or ""
        confirm_password = form.get("confirm_password") or ""

        if not full_name:
            return False, "Full name is required."

        if not username:
            return False, "Username is required."

        if not password:
            return False, "Password is required."

        if password != confirm_password:
            return False, "Passwords do not match."

        if UserService.username_exists(username):
            return False, "Username already exists."

        if UserService.email_exists(email):
            return False, "Email already exists."

        if UserService.phone_exists(phone):
            return False, "Phone number already exists."

        try:
            role_id = int(form["role_id"])
        except (KeyError, TypeError, ValueError):
            return False, "Please select a valid role."

        # Administrator-created users are accepted immediately.
        # There is no separate approval step.
        user = User(
            full_name=full_name,
            username=username,
            email=email,
            phone=phone,
            role_id=role_id,
            is_active=True,
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return True, "User created successfully and activated."

    # ==========================================
    # UPDATE USER
    # ==========================================

    @staticmethod
    def update_user(user, form):

        username = UserService.normalize_username(form.get("username"))
        email = UserService.normalize_email(form.get("email"))
        phone = UserService.normalize_phone(form.get("phone"))

        if not username:
            return False, "Username is required."

        if UserService.username_exists(username, user.id):
            return False, "Username already exists."

        if UserService.email_exists(email, user.id):
            return False, "Email already exists."

        if UserService.phone_exists(phone, user.id):
            return False, "Phone number already exists."

        new_password = form.get("password") or ""
        confirm_password = form.get("confirm_password") or ""

        if new_password or confirm_password:
            if new_password != confirm_password:
                return False, "Passwords do not match."

            if not new_password:
                return False, "Password cannot be empty."

            user.set_password(new_password)

        user.full_name = (form.get("full_name") or "").strip()
        user.username = username
        user.email = email
        user.phone = phone
        user.role_id = int(form["role_id"])
        user.is_active = form.get("is_active", "1") == "1"

        db.session.commit()

        return True, "User updated successfully."


    # ==========================================
    # SELF-SERVICE PROFILE
    # ==========================================

    @staticmethod
    def update_own_profile(user, form):

        full_name = (form.get("full_name") or "").strip()
        username = UserService.normalize_username(form.get("username"))
        email = UserService.normalize_email(form.get("email"))
        phone = UserService.normalize_phone(form.get("phone"))

        if not full_name:
            return False, "Full name is required."

        if not username:
            return False, "Username is required."

        if UserService.username_exists(username, user.id):
            return False, "Username already exists."

        if UserService.email_exists(email, user.id):
            return False, "Email already exists."

        if UserService.phone_exists(phone, user.id):
            return False, "Phone number already exists."

        user.full_name = full_name
        user.username = username
        user.email = email
        user.phone = phone

        db.session.commit()
        return True, "Profile updated successfully."

    @staticmethod
    def change_own_password(user, password):
        if not password:
            return False, "New password cannot be empty."

        if len(password) < 8:
            return False, "New password must be at least 8 characters long."

        if password == "":
            return False, "New password cannot be empty."

        user.set_password(password)
        db.session.commit()
        return True, "Password changed successfully."

    # ==========================================
    # CHANGE PASSWORD
    # ==========================================

    @staticmethod
    def change_password(user, password):

        user.set_password(password)
        db.session.commit()

        return True

    # ==========================================
    # TOGGLE STATUS
    # ==========================================

    @staticmethod
    def toggle_status(user):

        user.is_active = not user.is_active

        db.session.commit()

        return True
