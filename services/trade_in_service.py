from decimal import Decimal


from db import db

from models.customer import Customer
from models.trade_in import TradeIn
from models.trade_in_item import TradeInItem
from models.product_variant import ProductVariant
from models.imei import IMEI

from utils.timezone import application_now


class TradeInService:

    # ============================================================
    # GENERATE TRADE-IN NUMBER
    # ============================================================

    @staticmethod
    def generate_trade_in_number():

        year = application_now().year

        last = TradeIn.query.order_by(TradeIn.id.desc()).first()

        if last:

            try:

                number = int(last.trade_in_number.split("-")[-1])

            except Exception:

                number = 0

        else:

            number = 0

        return f"TRD-{year}-{number + 1:06d}"

    # ============================================================
    # CREATE TRADE-IN
    # ============================================================

    @staticmethod
    def create_trade_in(customer_id, customer_data, items, created_by):

        try:

            customer = None

            if customer_id:

                customer = Customer.query.get(int(customer_id))

                if not customer:

                    raise Exception("Selected customer was not found.")

                customer_data["customer_name"] = customer.full_name

                customer_data["phone_number"] = customer.phone

                customer_data["alternative_phone"] = customer.alternative_phone

                customer_data["business_name"] = customer.business_name

                customer_data["email"] = customer.email

                customer_data["national_id"] = customer.national_id

                customer_data["address"] = customer.address

            trade = TradeIn(
                trade_in_number=TradeInService.generate_trade_in_number(),
                customer_id=customer.id if customer else None,
                customer_name=customer_data["customer_name"],
                phone_number=customer_data["phone_number"],
                alternative_phone=customer_data.get("alternative_phone"),
                business_name=customer_data.get("business_name"),
                email=customer_data.get("email"),
                national_id=customer_data.get("national_id"),
                address=customer_data.get("address"),
                trade_in_date=customer_data["trade_in_date"],
                cash_paid=Decimal(str(customer_data.get("cash_paid", 0))),
                topup_received=Decimal(str(customer_data.get("topup_received", 0))),
                notes=customer_data.get("notes"),
                created_by=created_by,
                status="Accepted",
                total_trade_value=Decimal("0.00"),
            )

            db.session.add(trade)

            db.session.flush()

            grand_total = Decimal("0.00")

            # ====================================================
            # SAVE DEVICES
            # ====================================================

            for item in items:

                variant = ProductVariant.query.get(item["product_variant_id"])

                if not variant:

                    raise Exception("Variant not found.")

                buying_price = Decimal(str(item["final_trade_value"]))

                selling_price = Decimal(str(item["default_selling_price"]))

                estimated_profit = selling_price - buying_price

                # ===============================================
                # CREATE IMEI
                # ===============================================

                imei_number = (item.get("imei") or "").strip()
                if not imei_number:
                    raise Exception(
                        f"IMEI is required for trade-in device {variant.sku}."
                    )
                if IMEI.query.filter_by(imei=imei_number).first():
                    raise Exception(f"IMEI already exists: {imei_number}")

                imei = IMEI(
                    product_variant_id=variant.id,
                    imei=imei_number,
                    buying_price=buying_price,
                    default_selling_price=selling_price,
                    acquisition_source="Trade In",
                    received_date=application_now().replace(tzinfo=None),
                    status="In Stock",
                )

                db.session.add(imei)

                db.session.flush()

                # Increase stock

                variant.quantity += 1

                trade_item = TradeInItem(
                    trade_in_id=trade.id,
                    product_variant_id=variant.id,
                    imei_id=imei.id,
                    serial_number=item.get("serial_number"),
                    battery_health=item.get("battery_health"),
                    network_lock=item.get("network_lock"),
                    icloud_status=item.get("icloud_status"),
                    frp_status=item.get("frp_status"),
                    screen_condition=item.get("screen_condition"),
                    back_condition=item.get("back_condition"),
                    frame_condition=item.get("frame_condition"),
                    camera_condition=item.get("camera_condition"),
                    charging_port=item.get("charging_port"),
                    speaker_status=item.get("speaker_status"),
                    microphone_status=item.get("microphone_status"),
                    face_id_status=item.get("face_id_status"),
                    fingerprint_status=item.get("fingerprint_status"),
                    volume_buttons=item.get("volume_buttons"),
                    power_button=item.get("power_button"),
                    wifi_status=item.get("wifi_status"),
                    bluetooth_status=item.get("bluetooth_status"),
                    sim_status=item.get("sim_status"),
                    vibration_status=item.get("vibration_status"),
                    flashlight_status=item.get("flashlight_status"),
                    offered_value=Decimal(str(item["offered_value"])),
                    final_trade_value=buying_price,
                    default_selling_price=selling_price,
                    estimated_profit=estimated_profit,
                    box_received=item.get("box_received", False),
                    charger_received=item.get("charger_received", False),
                    cable_received=item.get("cable_received", False),
                    adapter_received=item.get("adapter_received", False),
                    earphones_received=item.get("earphones_received", False),
                    case_received=item.get("case_received", False),
                    screen_protector=item.get("screen_protector", False),
                    remarks=item.get("remarks"),
                )

                db.session.add(trade_item)

                grand_total += buying_price

            trade.total_trade_value = grand_total

            db.session.commit()

            return trade

        except Exception as e:

            db.session.rollback()

            raise e
