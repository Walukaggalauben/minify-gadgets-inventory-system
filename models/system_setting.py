from db import db


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)

    # -------------------------
    # General
    # -------------------------
    currency = db.Column(
        db.String(10),
        nullable=False,
        default="UGX"
    )

    timezone = db.Column(
        db.String(100),
        nullable=False,
        default="Africa/Kampala"
    )

    date_format = db.Column(
        db.String(30),
        nullable=False,
        default="DD/MM/YYYY"
    )

    # -------------------------
    # Inventory
    # -------------------------
    default_minimum_stock = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    enable_low_stock_alerts = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    prevent_negative_stock = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # -------------------------
    # Sales
    # -------------------------
    require_customer_on_sale = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    require_imei_when_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    allow_price_override = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # -------------------------
    # Receipt
    # -------------------------
    receipt_footer = db.Column(
        db.String(255),
        nullable=True,
        default="Thank you for shopping with us."
    )

    show_imei_on_receipt = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    show_cashier_on_receipt = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # -------------------------
    # Purchasing
    # -------------------------
    auto_update_buying_price = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # -------------------------
    # System
    # -------------------------
    records_per_page = db.Column(
        db.Integer,
        nullable=False,
        default=25
    )

    session_timeout_minutes = db.Column(
        db.Integer,
        nullable=False,
        default=60
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<SystemSetting {self.id}>"

    @classmethod
    def get_settings(cls):
        """
        Return the single system settings record.
        Create the default record automatically if it does not exist.
        """
        settings = cls.query.first()

        if settings is None:
            settings = cls()
            db.session.add(settings)
            db.session.commit()

        return settings