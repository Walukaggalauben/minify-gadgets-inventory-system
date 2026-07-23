from db import db


class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True)

    business_name = db.Column(
        db.String(150),
        nullable=False,
        default="MINIFY GADGETS"
    )

    tagline = db.Column(
        db.String(150),
        nullable=False,
        default="Phones & Accessories"
    )

    address = db.Column(
        db.String(255),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False
    )

    alternate_phone = db.Column(
        db.String(30)
    )

    email = db.Column(
        db.String(120)
    )

    website = db.Column(
        db.String(120)
    )

    logo = db.Column(
        db.String(255),
        default="default_logo.png"
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="UGX"
    )

    receipt_footer = db.Column(
        db.Text,
        default="Thank you for shopping with MINIFY GADGETS."
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<Company {self.business_name}>"