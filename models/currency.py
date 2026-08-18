from db import db


class Currency(db.Model):
    __tablename__ = "currencies"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(10),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    symbol = db.Column(
        db.String(10),
        nullable=False
    )

    decimal_places = db.Column(
        db.Integer,
        nullable=False,
        default=2
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<Currency {self.code}>"

    @property
    def display_name(self):
        return f"{self.code} — {self.name}"