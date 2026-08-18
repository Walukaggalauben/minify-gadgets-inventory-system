from db import db

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from datetime import datetime

from utils.auth import login_required

from models.trade_in import TradeIn
from models.product import Product
from models.product_variant import ProductVariant
from models.trade_in_item import TradeInItem
from models.imei import IMEI

from utils.timezone import application_date

from services.trade_in_service import TradeInService

trade_in_bp = Blueprint("trade_in", __name__, url_prefix="/trade-ins")


# ==========================================================
# INDEX
# ==========================================================


@trade_in_bp.route("/")
def index():

    if not login_required():
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "").strip()

    date_from = request.args.get("date_from")

    date_to = request.args.get("date_to")

    query = TradeIn.query

    # =====================================
    # SEARCH
    # =====================================

    if search:

        query = (
            query.outerjoin(TradeInItem)
            .outerjoin(IMEI)
            .outerjoin(ProductVariant)
            .outerjoin(Product)
            .filter(
                or_(
                    TradeIn.trade_in_number.ilike(f"%{search}%"),
                    TradeIn.customer_name.ilike(f"%{search}%"),
                    TradeIn.phone_number.ilike(f"%{search}%"),
                    Product.name.ilike(f"%{search}%"),
                    IMEI.imei.ilike(f"%{search}%"),
                )
            )
            .distinct()
        )
    # =====================================
    # DATE FILTER
    # =====================================

    if date_from:

        query = query.filter(TradeIn.trade_in_date >= date_from)

    if date_to:

        query = query.filter(TradeIn.trade_in_date <= date_to)

    trade_ins = query.order_by(TradeIn.trade_in_date.desc()).all()

    return render_template(
        "trade_ins/index.html",
        trade_ins=trade_ins,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


# ==========================================================
# CREATE
# ==========================================================


@trade_in_bp.route("/create", methods=["GET", "POST"])
def create():

    if not login_required():
        return redirect(url_for("auth.login"))

    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()

    variants = ProductVariant.query.filter_by(is_active=True).all()

    if request.method == "POST":

        customer_data = {
            "customer_name": request.form.get("customer_name"),
            "phone_number": request.form.get("phone_number"),
            "alternative_phone": request.form.get("alternative_phone"),
            "business_name": request.form.get("business_name"),
            "email": request.form.get("email"),
            "national_id": request.form.get("national_id"),
            "address": request.form.get("address"),
            "trade_in_date": datetime.strptime(
                request.form.get("trade_in_date"), "%Y-%m-%d"
            ).date(),
            "cash_paid": float(request.form.get("cash_paid", 0) or 0),
            "topup_received": float(request.form.get("topup_received", 0) or 0),
            "notes": request.form.get("notes"),
        }

        items = []

        variant_ids = request.form.getlist("variant_id[]")
        imeis = request.form.getlist("imei[]")
        serial_numbers = request.form.getlist("serial_number[]")

        battery_healths = request.form.getlist("battery_health[]")

        screen_conditions = request.form.getlist("screen_condition[]")

        back_conditions = request.form.getlist("back_condition[]")

        frame_conditions = request.form.getlist("frame_condition[]")

        camera_conditions = request.form.getlist("camera_condition[]")

        charging_ports = request.form.getlist("charging_port[]")

        speaker_statuses = request.form.getlist("speaker_status[]")

        microphone_statuses = request.form.getlist("microphone_status[]")

        face_id_statuses = request.form.getlist("face_id_status[]")

        fingerprint_statuses = request.form.getlist("fingerprint_status[]")

        wifi_statuses = request.form.getlist("wifi_status[]")

        bluetooth_statuses = request.form.getlist("bluetooth_status[]")

        sim_statuses = request.form.getlist("sim_status[]")

        offered_values = request.form.getlist("offered_value[]")

        final_trade_values = request.form.getlist("final_trade_value[]")

        selling_prices = request.form.getlist("default_selling_price[]")

        remarks = request.form.getlist("remarks[]")

        for i, variant_id in enumerate(variant_ids):

            if not variant_id:
                continue

            items.append(
                {
                    "product_variant_id": int(variant_id),
                    "imei": imeis[i] if i < len(imeis) else "",
                    "serial_number": (
                        serial_numbers[i] if i < len(serial_numbers) else ""
                    ),
                    "battery_health": (
                        battery_healths[i] if i < len(battery_healths) else None
                    ),
                    "screen_condition": (
                        screen_conditions[i] if i < len(screen_conditions) else ""
                    ),
                    "back_condition": (
                        back_conditions[i] if i < len(back_conditions) else ""
                    ),
                    "frame_condition": (
                        frame_conditions[i] if i < len(frame_conditions) else ""
                    ),
                    "camera_condition": (
                        camera_conditions[i] if i < len(camera_conditions) else ""
                    ),
                    "charging_port": (
                        charging_ports[i] if i < len(charging_ports) else ""
                    ),
                    "speaker_status": (
                        speaker_statuses[i] if i < len(speaker_statuses) else ""
                    ),
                    "microphone_status": (
                        microphone_statuses[i] if i < len(microphone_statuses) else ""
                    ),
                    "face_id_status": (
                        face_id_statuses[i] if i < len(face_id_statuses) else ""
                    ),
                    "fingerprint_status": (
                        fingerprint_statuses[i] if i < len(fingerprint_statuses) else ""
                    ),
                    "wifi_status": wifi_statuses[i] if i < len(wifi_statuses) else "",
                    "bluetooth_status": (
                        bluetooth_statuses[i] if i < len(bluetooth_statuses) else ""
                    ),
                    "sim_status": sim_statuses[i] if i < len(sim_statuses) else "",
                    "offered_value": (
                        offered_values[i] if i < len(offered_values) else 0
                    ),
                    "final_trade_value": (
                        final_trade_values[i] if i < len(final_trade_values) else 0
                    ),
                    "default_selling_price": (
                        selling_prices[i] if i < len(selling_prices) else 0
                    ),
                    "remarks": remarks[i] if i < len(remarks) else "",
                    "box_received": f"box_received_{i}" in request.form,
                    "charger_received": f"charger_received_{i}" in request.form,
                    "cable_received": f"cable_received_{i}" in request.form,
                    "adapter_received": f"adapter_received_{i}" in request.form,
                    "earphones_received": f"earphones_received_{i}" in request.form,
                    "case_received": f"case_received_{i}" in request.form,
                    "screen_protector": f"screen_protector_{i}" in request.form,
                }
            )

        try:

            TradeInService.create_trade_in(
                customer_id=request.form.get("customer_id"),
                customer_data=customer_data,
                items=items,
                created_by=session["user_id"],
            )

            flash("Trade-In created successfully.", "success")

            return redirect(url_for("trade_in.index"))

        except Exception as e:

            import traceback

            traceback.print_exc()

            flash(str(e), "danger")

    return render_template(
        "trade_ins/create.html",
        products=products,
        variants=variants,
        today=application_date().strftime("%Y-%m-%d"),
    )
    # ==========================================================


# VIEW
# ==========================================================


@trade_in_bp.route("/view/<int:id>")
def view(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    trade_in = TradeIn.query.get_or_404(id)

    return render_template("trade_ins/view.html", trade_in=trade_in)


# ==========================================================
# PRINT
# ==========================================================


@trade_in_bp.route("/print/<int:id>")
def print_trade_in(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    trade_in = TradeIn.query.get_or_404(id)

    return render_template("trade_ins/print.html", trade_in=trade_in)


# ==========================================================
# DELETE
# ==========================================================


@trade_in_bp.route("/delete/<int:id>")
def delete(id):

    if not login_required():
        return redirect(url_for("auth.login"))

    trade_in = TradeIn.query.get_or_404(id)

    try:

        # A trade-in cannot be deleted after its device has already been sold.
        for item in trade_in.items:
            if item.imei and item.imei.status == "Sold":
                raise Exception(
                    "This trade-in contains a device that has already been sold and cannot be deleted."
                )

        # Restore stock before deleting.
        for item in trade_in.items:
            if item.imei:
                db.session.delete(item.imei)
            if item.product_variant:
                item.product_variant.quantity -= 1

        db.session.delete(trade_in)

        db.session.commit()

        flash("Trade-In deleted successfully.", "success")

    except Exception as e:

        db.session.rollback()

        flash(str(e), "danger")

    return redirect(url_for("trade_in.index"))


# ==========================================================
# SEARCH PRODUCTS API
# ==========================================================

from flask import jsonify
from sqlalchemy import or_


@trade_in_bp.route("/api/search-products")
def search_products():

    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    products = (
        Product.query.filter(Product.is_active == True, Product.name.ilike(f"%{q}%"))
        .order_by(Product.name)
        .limit(15)
        .all()
    )

    return jsonify([{"id": p.id, "name": p.name} for p in products])


# ==========================================================
# PRODUCT VARIANTS API
# ==========================================================


@trade_in_bp.route("/api/product/<int:product_id>/variants")
def product_variants(product_id):

    variants = (
        ProductVariant.query.filter_by(product_id=product_id, is_active=True)
        .order_by(ProductVariant.storage, ProductVariant.ram)
        .all()
    )

    data = []

    for variant in variants:

        data.append(
            {
                "id": variant.id,
                "brand": variant.product.brand.name,
                "model": variant.product.name,
                "storage": variant.storage or "",
                "ram": variant.ram or "",
                "colour": variant.colour or "",
                "sku": variant.sku,
                "stock": variant.quantity,
                "condition": variant.condition,
                "selling_price": float(variant.selling_price),
            }
        )

    return jsonify(data)


# ==========================================================
# TRADE-IN VALUATION API
# ==========================================================

from flask import jsonify

from services.trade_in_valuation_service import TradeInValuationService


@trade_in_bp.route("/api/valuation", methods=["POST"])
def valuation():

    data = request.get_json()

    result = TradeInValuationService.calculate(
        selling_price=data.get("selling_price", 0),
        battery_health=data.get("battery_health"),
        screen_condition=data.get("screen_condition"),
        back_condition=data.get("back_condition"),
        frame_condition=data.get("frame_condition"),
        camera_condition=data.get("camera_condition"),
        face_id_status=data.get("face_id_status"),
        fingerprint_status=data.get("fingerprint_status"),
        network_lock=data.get("network_lock"),
        icloud_status=data.get("icloud_status"),
        frp_status=data.get("frp_status"),
        charger_received=data.get("charger_received", True),
        box_received=data.get("box_received", True),
    )

    return jsonify(
        {
            "suggested_trade_value": float(result["suggested_trade_value"]),
            "expected_profit": float(result["expected_profit"]),
            "total_deduction": float(result["total_deduction"]),
            "deductions": result["deductions"],
        }
    )
