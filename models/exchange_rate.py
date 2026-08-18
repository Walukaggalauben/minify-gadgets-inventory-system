from utils.timezone import utc_now_naive

from db import db


class ExchangeRate(db.Model):
    __tablename__ = "exchange_rates"

    id = db.Column(db.Integer, primary_key=True)

    from_currency_id = db.Column(
        db.Integer, db.ForeignKey("currencies.id"), nullable=False
    )

    to_currency_id = db.Column(
        db.Integer, db.ForeignKey("currencies.id"), nullable=False
    )

    rate = db.Column(db.Numeric(20, 8), nullable=False)

    effective_at = db.Column(db.DateTime, nullable=False, default=utc_now_naive)

    source = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    from_currency = db.relationship("Currency", foreign_keys=[from_currency_id])

    to_currency = db.relationship("Currency", foreign_keys=[to_currency_id])

    def __repr__(self):
        return (
            f"<ExchangeRate "
            f"{self.from_currency.code if self.from_currency else '?'}"
            f"/"
            f"{self.to_currency.code if self.to_currency else '?'}"
            f"={self.rate}>"
        )
