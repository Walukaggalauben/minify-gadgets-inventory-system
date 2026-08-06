from db import db

from models.trade_in_rule import TradeInRule


class TradeInRuleService:

    @staticmethod
    def seed_defaults():

        if TradeInRule.query.count() > 0:
            return

        defaults = [
            ("Battery Below 80%", 150000, "Battery health below 80%"),
            ("Cracked Screen", 350000, "Display has cracks"),
            ("Back Damage", 150000, "Back glass damaged"),
            ("Frame Damage", 100000, "Frame dents or scratches"),
            ("Camera Fault", 200000, "Camera not working"),
            ("Face ID Fault", 250000, "Face ID unavailable"),
            ("Fingerprint Fault", 150000, "Fingerprint sensor faulty"),
            ("Network Locked", 200000, "Carrier locked"),
            ("FRP/iCloud Locked", 500000, "Activation lock enabled"),
            ("No Charger", 30000, "No charger returned"),
            ("No Box", 20000, "Original box missing"),
        ]

        for name, amount, description in defaults:

            db.session.add(
                TradeInRule(
                    rule_name=name, deduction_amount=amount, description=description
                )
            )

        db.session.commit()
