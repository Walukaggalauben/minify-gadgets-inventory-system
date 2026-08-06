from db import db


class TradeInRule(db.Model):
    __tablename__ = "trade_in_rules"

    id = db.Column(db.Integer, primary_key=True)

    rule_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    deduction_amount = db.Column(
        db.Numeric(15, 2),
        nullable=False,
        default=0
    )

    description = db.Column(
        db.String(255)
    )

    is_active = db.Column(
        db.Boolean,
        default=True
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
        return f"<TradeInRule {self.rule_name}>"