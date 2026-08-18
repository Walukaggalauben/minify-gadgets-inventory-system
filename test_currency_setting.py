from app import create_app
from db import db
from models.system_setting import SystemSetting
from models.currency import Currency


app = create_app()

with app.app_context():

    settings = SystemSetting.get_settings()

    original_currency = settings.currency

    print(
        "ORIGINAL CURRENCY:",
        original_currency
    )

    usd = Currency.query.filter_by(
        code="USD",
        is_active=True
    ).first()

    if not usd:
        raise Exception(
            "Active USD currency was not found."
        )

    print(
        "TEST CURRENCY:",
        usd.code
    )

    try:

        # ==========================================
        # CHANGE TO USD
        # ==========================================

        settings.currency = usd.code
        db.session.commit()

        print(
            "CURRENCY AFTER CHANGE:",
            settings.currency
        )

        if settings.currency == "USD":

            print(
                "PASS: CURRENCY CHANGED TO USD"
            )

        else:

            print(
                "FAIL: CURRENCY DID NOT CHANGE"
            )

        # ==========================================
        # VERIFY DATABASE CURRENCY EXISTS
        # ==========================================

        selected = Currency.query.filter_by(
            code=settings.currency
        ).first()

        if selected:

            print(
                "PASS: SELECTED CURRENCY EXISTS"
            )

            print(
                "CURRENCY NAME:",
                selected.name
            )

            print(
                "CURRENCY SYMBOL:",
                selected.symbol
            )

        else:

            print(
                "FAIL: SELECTED CURRENCY NOT FOUND"
            )

    finally:

        # ==========================================
        # RESTORE ORIGINAL CURRENCY
        # ==========================================

        settings.currency = original_currency
        db.session.commit()

        print(
            "CURRENCY RESTORED:",
            settings.currency
        )

        if settings.currency == original_currency:

            print(
                "PASS: ORIGINAL CURRENCY RESTORED"
            )

        else:

            print(
                "FAIL: ORIGINAL CURRENCY NOT RESTORED"
            )