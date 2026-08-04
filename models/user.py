from db import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(150), unique=True)

    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20))

    profile_photo = db.Column(db.String(255))

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    last_login = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    role = db.relationship(
        "Role",
        backref="users"
    )
    
    purchases = db.relationship(
    "Purchase",
    back_populates="user",
    lazy=True
    )
    
    sales = db.relationship(
    "Sale",
    back_populates="user",
    lazy=True
    )
    
    trade_ins = db.relationship(
    "TradeIn",
    back_populates="creator",
    cascade="all, delete-orphan"
)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password,
            password
        )
        
        

    def __repr__(self):
        return f"<User {self.username}>"