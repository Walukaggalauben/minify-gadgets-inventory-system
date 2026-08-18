from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from utils.timezone import utc_now_naive

import requests

from db import db
from models.currency import Currency
from models.exchange_rate import ExchangeRate


class CurrencyService:

    DEFAULT_CURRENCIES = [
        {
            "code": "UGX",
            "name": "Uganda Shilling",
            "symbol": "UGX",
            "decimal_places": 0,
        },
        {
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$",
            "decimal_places": 2,
        },
        {
            "code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "decimal_places": 2,
        },
        {
            "code": "GBP",
            "name": "British Pound",
            "symbol": "£",
            "decimal_places": 2,
        },
        {
            "code": "KES",
            "name": "Kenyan Shilling",
            "symbol": "KES",
            "decimal_places": 2,
        },
        {
            "code": "TZS",
            "name": "Tanzanian Shilling",
            "symbol": "TZS",
            "decimal_places": 0,
        },
        {
            "code": "RWF",
            "name": "Rwandan Franc",
            "symbol": "RWF",
            "decimal_places": 0,
        },
    ]

    # ExchangeRate-API Open Access endpoint
    RATE_API_URL = "https://open.er-api.com/v6/latest"

    # How long a stored rate can be reused before
    # requesting another rate.
    RATE_CACHE_MINUTES = 30

    # ==========================================
    # CURRENCY MANAGEMENT
    # ==========================================

    @classmethod
    def seed_default_currencies(cls):

        changed = False

        for data in cls.DEFAULT_CURRENCIES:

            currency = Currency.query.filter_by(code=data["code"]).first()

            if currency is None:

                currency = Currency(
                    code=data["code"],
                    name=data["name"],
                    symbol=data["symbol"],
                    decimal_places=data["decimal_places"],
                    is_active=True,
                )

                db.session.add(currency)

                changed = True

        if changed:
            db.session.commit()

    @staticmethod
    def get_active_currencies():

        return (
            Currency.query.filter_by(is_active=True).order_by(Currency.code.asc()).all()
        )

    @staticmethod
    def get_by_code(code):

        if not code:
            return None

        return Currency.query.filter(
            db.func.upper(Currency.code) == code.strip().upper()
        ).first()

    # ==========================================
    # AMOUNT VALIDATION
    # ==========================================

    @staticmethod
    def validate_amount(amount):

        try:

            value = Decimal(str(amount))

            if value < 0:
                raise ValueError("Amount cannot be negative.")

            return value

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:

            raise ValueError("Invalid monetary amount.") from error

    # ==========================================
    # DIRECT CONVERSION
    # ==========================================

    @staticmethod
    def convert(amount, rate):

        amount = CurrencyService.validate_amount(amount)

        try:

            rate = Decimal(str(rate))

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:

            raise ValueError("Invalid exchange rate.") from error

        if rate <= 0:

            raise ValueError("Exchange rate must be greater than zero.")

        return amount * rate

    # ==========================================
    # STORED RATE
    # ==========================================

    @staticmethod
    def get_stored_rate(
        from_currency,
        to_currency,
        max_age_minutes=None,
    ):

        if max_age_minutes is None:
            max_age_minutes = CurrencyService.RATE_CACHE_MINUTES

        cutoff = utc_now_naive() - timedelta(minutes=max_age_minutes)
        return (
            ExchangeRate.query.filter(
                ExchangeRate.from_currency_id == from_currency.id,
                ExchangeRate.to_currency_id == to_currency.id,
                ExchangeRate.effective_at >= cutoff,
            )
            .order_by(ExchangeRate.effective_at.desc())
            .first()
        )

    # ==========================================
    # FETCH LIVE RATE
    # ==========================================

    @staticmethod
    def fetch_live_rate(
        from_currency_code,
        to_currency_code,
    ):

        from_currency_code = from_currency_code.strip().upper()

        to_currency_code = to_currency_code.strip().upper()

        if from_currency_code == to_currency_code:
            return Decimal("1")

        url = f"{CurrencyService.RATE_API_URL}/" f"{from_currency_code}"

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":

            raise ValueError(
                data.get(
                    "error-type",
                    "Exchange-rate API request failed.",
                )
            )

        rates = data.get("rates", {})

        rate = rates.get(to_currency_code)

        if rate is None:

            raise ValueError(
                f"No exchange rate returned for "
                f"{from_currency_code} to "
                f"{to_currency_code}."
            )

        try:

            rate = Decimal(str(rate))

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:

            raise ValueError("Invalid exchange rate received.") from error

        if rate <= 0:

            raise ValueError("Exchange rate must be greater than zero.")

        return rate

    # ==========================================
    # GET RATE
    # ==========================================

    @classmethod
    def get_rate(
        cls,
        from_currency_code,
        to_currency_code,
        force_refresh=False,
    ):

        from_currency_code = from_currency_code.strip().upper()

        to_currency_code = to_currency_code.strip().upper()

        from_currency = cls.get_by_code(from_currency_code)

        to_currency = cls.get_by_code(to_currency_code)

        if from_currency is None:

            raise ValueError(f"Unsupported currency: " f"{from_currency_code}")

        if to_currency is None:

            raise ValueError(f"Unsupported currency: " f"{to_currency_code}")

        if from_currency.id == to_currency.id:

            return Decimal("1")

        # ------------------------------------------
        # Use recently stored rate
        # ------------------------------------------

        if not force_refresh:

            stored_rate = cls.get_stored_rate(
                from_currency,
                to_currency,
            )

            if stored_rate:

                return Decimal(str(stored_rate.rate))

        # ------------------------------------------
        # Fetch new rate
        # ------------------------------------------

        rate = cls.fetch_live_rate(
            from_currency.code,
            to_currency.code,
        )

        # ------------------------------------------
        # Save rate
        # ------------------------------------------

        exchange_rate = ExchangeRate(
            from_currency_id=from_currency.id,
            to_currency_id=to_currency.id,
            rate=rate,
            effective_at=utc_now_naive(),
            source="ExchangeRate-API",
        )

        db.session.add(exchange_rate)
        db.session.commit()

        return rate

    # ==========================================
    # CONVERT CURRENCY
    # ==========================================

    @classmethod
    def convert_currency(
        cls,
        amount,
        from_currency_code,
        to_currency_code,
        force_refresh=False,
    ):

        amount = cls.validate_amount(amount)

        rate = cls.get_rate(
            from_currency_code,
            to_currency_code,
            force_refresh=force_refresh,
        )

        converted_amount = cls.convert(
            amount,
            rate,
        )

        return {
            "amount": amount,
            "from_currency": (from_currency_code.upper()),
            "to_currency": (to_currency_code.upper()),
            "rate": rate,
            "converted_amount": converted_amount,
        }
