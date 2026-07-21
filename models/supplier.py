from db import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    contact_person = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(30)
    )

    email = db.Column(
        db.String(120)
    )

    address = db.Column(
        db.Text
    )

    notes = db.Column(
        db.Text
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
    
    purchases = db.relationship(
    "Purchase",
    back_populates="supplier",
    lazy=True
    )

    def __repr__(self):
        return f"<Supplier {self.name}>"