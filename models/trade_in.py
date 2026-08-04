from db import db


class TradeIn(db.Model):
    __tablename__ = "trade_ins"

    id = db.Column(db.Integer, primary_key=True)

    trade_in_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    # ==========================================
    # CUSTOMER INFORMATION
    # ==========================================

    customer_name = db.Column(
        db.String(150),
        nullable=False
    )

    phone_number = db.Column(
        db.String(30),
        nullable=False
    )

    alternative_phone = db.Column(
        db.String(30)
    )

    business_name = db.Column(
        db.String(150)
    )

    email = db.Column(
        db.String(150)
    )

    national_id = db.Column(
        db.String(100)
    )

    address = db.Column(
        db.Text
    )

    # ==========================================
    # TRADE INFORMATION
    # ==========================================

    trade_in_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.Enum(
            "Pending",
            "Accepted",
            "Rejected",
            "Cancelled",
            name="trade_in_status"
        ),
        default="Pending",
        nullable=False
    )

    total_trade_value = db.Column(
        db.Numeric(15, 2),
        default=0
    )

    cash_paid = db.Column(
        db.Numeric(15, 2),
        default=0
    )

    topup_received = db.Column(
        db.Numeric(15, 2),
        default=0
    )

    notes = db.Column(
        db.Text
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
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

    creator = db.relationship(
        "User",
        back_populates="trade_ins"
    )

    items = db.relationship(
        "TradeInItem",
        back_populates="trade_in",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TradeIn {self.trade_in_number}>"