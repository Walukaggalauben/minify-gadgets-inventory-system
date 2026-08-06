from decimal import Decimal

from models.trade_in_rule import TradeInRule


class TradeInValuationService:

    @staticmethod
    def calculate(
        selling_price,
        battery_health=None,
        screen_condition=None,
        back_condition=None,
        frame_condition=None,
        camera_condition=None,
        face_id_status=None,
        fingerprint_status=None,
        network_lock=None,
        icloud_status=None,
        frp_status=None,
        charger_received=True,
        box_received=True,
    ):

        selling_price = Decimal(str(selling_price))

        deductions = []

        total_deduction = Decimal("0.00")

        rules = {
            rule.rule_name: Decimal(str(rule.deduction_amount))
            for rule in TradeInRule.query.filter_by(is_active=True).all()
        }

        def deduct(rule_name):
            nonlocal total_deduction

            amount = rules.get(rule_name)

            if amount:

                total_deduction += amount

                deductions.append(
                    {
                        "rule": rule_name,
                        "amount": amount,
                    }
                )

        # Battery
        if battery_health:

            if int(battery_health) < 80:
                deduct("Battery Below 80%")

        # Screen
        if screen_condition and screen_condition != "Excellent":
            deduct("Cracked Screen")

        # Back
        if back_condition and back_condition != "Excellent":
            deduct("Back Damage")

        # Frame
        if frame_condition and frame_condition != "Excellent":
            deduct("Frame Damage")

        # Camera
        if camera_condition and camera_condition != "Excellent":
            deduct("Camera Fault")

        # Face ID
        if face_id_status == "Faulty":
            deduct("Face ID Fault")

        # Fingerprint
        if fingerprint_status == "Faulty":
            deduct("Fingerprint Fault")

        # Network Lock
        if network_lock == "Locked":
            deduct("Network Locked")

        # iCloud
        if icloud_status == "Locked":
            deduct("FRP/iCloud Locked")

        # FRP
        if frp_status == "Locked":
            deduct("FRP/iCloud Locked")

        # Accessories
        if not charger_received:
            deduct("No Charger")

        if not box_received:
            deduct("No Box")

        suggested_value = selling_price - total_deduction

        if suggested_value < 0:
            suggested_value = Decimal("0.00")

        expected_profit = selling_price - suggested_value

        return {
            "selling_price": selling_price,
            "deductions": deductions,
            "total_deduction": total_deduction,
            "suggested_trade_value": suggested_value,
            "expected_profit": expected_profit,
        }
