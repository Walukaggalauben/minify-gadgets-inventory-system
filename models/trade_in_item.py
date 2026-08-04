from db import db


class TradeInItem(db.Model):
    __tablename__ = "trade_in_items"

    id = db.Column(db.Integer, primary_key=True)

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    trade_in_id = db.Column(
        db.Integer,
        db.ForeignKey("trade_ins.id"),
        nullable=False
    )

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id"),
        nullable=False
    )

    imei_id = db.Column(
        db.Integer,
        db.ForeignKey("imeis.id"),
        nullable=True
    )

    # ============================================================
    # DEVICE INFORMATION
    # ============================================================

    serial_number = db.Column(
        db.String(100)
    )

    battery_health = db.Column(
        db.Integer
    )

    network_lock = db.Column(
        db.String(100)
    )

    icloud_status = db.Column(
        db.String(100)
    )

    frp_status = db.Column(
        db.String(100)
    )

    # ============================================================
    # PHYSICAL INSPECTION
    # ============================================================

    screen_condition = db.Column(
        db.String(100)
    )

    back_condition = db.Column(
        db.String(100)
    )

    frame_condition = db.Column(
        db.String(100)
    )

    camera_condition = db.Column(
        db.String(100)
    )

    charging_port = db.Column(
        db.String(100)
    )

    speaker_status = db.Column(
        db.String(100)
    )

    microphone_status = db.Column(
        db.String(100)
    )

    face_id_status = db.Column(
        db.String(100)
    )

    fingerprint_status = db.Column(
        db.String(100)
    )

    volume_buttons = db.Column(
        db.String(100)
    )

    power_button = db.Column(
        db.String(100)
    )

    wifi_status = db.Column(
        db.String(100)
    )

    bluetooth_status = db.Column(
        db.String(100)
    )

    sim_status = db.Column(
        db.String(100)
    )

    vibration_status = db.Column(
        db.String(100)
    )

    flashlight_status = db.Column(
        db.String(100)
    )

    # ============================================================
    # BUSINESS VALUES
    # ============================================================

    offered_value = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    final_trade_value = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    default_selling_price = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    estimated_profit = db.Column(
        db.Numeric(15, 2),
        default=0
    )

    # ============================================================
    # ACCESSORIES
    # ============================================================

    box_received = db.Column(
        db.Boolean,
        default=False
    )

    charger_received = db.Column(
        db.Boolean,
        default=False
    )

    cable_received = db.Column(
        db.Boolean,
        default=False
    )

    adapter_received = db.Column(
        db.Boolean,
        default=False
    )

    earphones_received = db.Column(
        db.Boolean,
        default=False
    )

    case_received = db.Column(
        db.Boolean,
        default=False
    )

    screen_protector = db.Column(
        db.Boolean,
        default=False
    )

    # ============================================================
    # NOTES
    # ============================================================

    remarks = db.Column(
        db.Text
    )

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    trade_in = db.relationship(
        "TradeIn",
        back_populates="items"
    )

    product_variant = db.relationship(
        "ProductVariant",
        back_populates="trade_in_items"
    )

    imei = db.relationship(
        "IMEI",
        back_populates="trade_in_item"
    )

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __repr__(self):
        return (
            f"<TradeInItem "
            f"id={self.id}, "
            f"variant={self.product_variant_id}, "
            f"value={self.final_trade_value}>"
        )