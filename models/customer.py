from db import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)

    customer_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
    )

    full_name = db.Column(
        db.String(150),
        nullable=False,
    )

    phone = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
    )

    alternative_phone = db.Column(
        db.String(30),
    )

    email = db.Column(
        db.String(120),
    )

    national_id = db.Column(
        db.String(50),
    )

    address = db.Column(
        db.Text,
    )

    business_name = db.Column(
        db.String(150),
    )

    customer_type = db.Column(
        db.Enum(
            "Retail",
            "Wholesale",
            "Corporate",
            "VIP",
            name="customer_type",
        ),
        default="Retail",
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

   

    def __repr__(self):
        return f"<Customer {self.customer_code}>"