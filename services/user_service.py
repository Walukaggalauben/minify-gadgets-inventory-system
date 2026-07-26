from sqlalchemy import or_


from db import db
from models.user import User
from models.role import Role


class UserService:

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
    def username_exists(
        username,
        exclude_id=None,
    ):

        query = User.query.filter_by(
            username=username
        )

        if exclude_id:

            query = query.filter(
                User.id != exclude_id
            )

        return query.first() is not None

    @staticmethod
    def email_exists(
        email,
        exclude_id=None,
    ):

        if not email:
            return False

        query = User.query.filter_by(
            email=email
        )

        if exclude_id:

            query = query.filter(
                User.id != exclude_id
            )

        return query.first() is not None

    # ==========================================
    # CREATE USER
    # ==========================================

    @staticmethod
    def create_user(form):

        if UserService.username_exists(
            form["username"]
        ):
            return False, "Username already exists."

        if UserService.email_exists(
            form.get("email")
        ):
            return False, "Email already exists."

        user = User(
            full_name=form["full_name"],
            username=form["username"],
            email=form.get("email"),
            phone=form.get("phone"),
            role_id=int(form["role_id"]),
            is_active=form.get("is_active", "1") == "1",
        )

        user.set_password(
            form["password"]
        )

        db.session.add(user)
        db.session.commit()

        return True, "User created successfully."

    # ==========================================
    # UPDATE USER
    # ==========================================

    @staticmethod
    def update_user(
        user,
        form
    ):

        if UserService.username_exists(
            form["username"],
            user.id,
        ):
            return False, "Username already exists."

        if UserService.email_exists(
            form.get("email"),
            user.id,
        ):
            return False, "Email already exists."

        user.full_name = form["full_name"]
        user.username = form["username"]
        user.email = form.get("email")
        user.phone = form.get("phone")
        user.role_id = int(form["role_id"])
        user.is_active = form.get("is_active", "1") == "1"

        db.session.commit()

        return True, "User updated successfully."

    # ==========================================
    # CHANGE PASSWORD
    # ==========================================

    @staticmethod
    def change_password(
        user,
        password,
    ):

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