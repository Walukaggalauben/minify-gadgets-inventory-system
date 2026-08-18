from sqlalchemy import func

from db import db
from models.sale_payment import SalePayment
from utils.timezone import application_now


class ReceiptService:

    # ==========================================================
    # RECEIPT NUMBER
    # ==========================================================

    @staticmethod
    def generate_receipt_number():
        """
        Generate the next sequential receipt number.

        Example:
        RCT-2026-000018

        Receipt numbers are independent from invoice numbers.
        Every SalePayment receives its own receipt number.
        """

        year = application_now().year
        prefix = f"RCT-{year}-"

        last_receipt = (
            SalePayment.query.filter(SalePayment.receipt_number.like(f"{prefix}%"))
            .order_by(SalePayment.receipt_number.desc())
            .first()
        )

        if not last_receipt:
            next_number = 1
        else:
            try:
                last_number = int(last_receipt.receipt_number.split("-")[-1])
                next_number = last_number + 1
            except (ValueError, AttributeError):
                next_number = 1

        receipt_number = f"{prefix}{next_number:06d}"

        # ======================================================
        # COLLISION PROTECTION
        # ======================================================

        while (
            SalePayment.query.filter_by(receipt_number=receipt_number).first()
            is not None
        ):
            next_number += 1
            receipt_number = f"{prefix}{next_number:06d}"

        return receipt_number
