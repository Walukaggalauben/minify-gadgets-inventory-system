from flask import Blueprint, render_template, request, jsonify
from utils.permissions import permission_required
from sqlalchemy import or_
from models.product_variant import ProductVariant
from models.imei import IMEI
from models.product import Product
from models.brand import Brand

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.route("/")
@permission_required("inventory.view")
def index():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = ProductVariant.query.join(ProductVariant.product)

    # ==========================================================
    # SEARCH
    # ==========================================================
    if search:
        query = query.filter(
            or_(
                ProductVariant.sku.ilike(f"%{search}%"),
                ProductVariant.barcode.ilike(f"%{search}%"),
                ProductVariant.product.has(Product.name.ilike(f"%{search}%")),
                ProductVariant.product.has(
                    Product.brand.has(Brand.name.ilike(f"%{search}%"))
                ),
            )
        )

    # ==========================================================
    # STOCK FILTER
    # ==========================================================
    if status == "low":
        query = query.filter(ProductVariant.quantity <= ProductVariant.minimum_stock)

    elif status == "out":
        query = query.filter(ProductVariant.quantity <= 0)

    elif status == "in":
        query = query.filter(ProductVariant.quantity > ProductVariant.minimum_stock)

    variants = query.order_by(
        ProductVariant.quantity.asc(), ProductVariant.sku.asc()
    ).all()

    # ==========================================================
    # INVENTORY SUMMARY
    # ==========================================================

    all_variants = ProductVariant.query.all()

    total_variants = len(all_variants)

    total_units = sum(int(v.quantity or 0) for v in all_variants)

    low_stock = sum(
        1 for v in all_variants if (v.quantity or 0) <= (v.minimum_stock or 0)
    )

    out_of_stock = sum(1 for v in all_variants if (v.quantity or 0) <= 0)

    # Total amount spent on stock currently available
    inventory_cost = sum(
        (v.buying_price or 0) * (v.quantity or 0) for v in all_variants
    )

    # Total amount the current stock could generate if everything
    # were sold at the normal selling price
    potential_sales = sum(
        (v.selling_price or 0) * (v.quantity or 0) for v in all_variants
    )

    # Expected gross profit from current stock
    expected_profit = potential_sales - inventory_cost

    imei_units = IMEI.query.filter(IMEI.status == "In Stock").count()

    summary = {
        "variants": total_variants,
        "units": total_units,
        "low": low_stock,
        "out": out_of_stock,
        "imei_units": imei_units,
        "inventory_cost": inventory_cost,
        "potential_sales": potential_sales,
        "expected_profit": expected_profit,
    }

    return render_template(
        "inventory/index.html",
        variants=variants,
        summary=summary,
        search=search,
        status=status,
    )


@inventory_bp.route("/api/barcode/<path:barcode>")
@permission_required("inventory.view")
def barcode_lookup(barcode):
    variant = ProductVariant.query.filter_by(barcode=barcode.strip()).first()
    if not variant:
        return jsonify({"found": False}), 404
    return jsonify(
        {
            "found": True,
            "id": variant.id,
            "sku": variant.sku,
            "barcode": variant.barcode,
            "product": variant.product.name,
            "brand": variant.product.brand.name,
            "stock": variant.quantity,
            "selling_price": float(variant.selling_price),
            "buying_price": float(variant.buying_price),
            "storage": variant.storage or "",
            "ram": variant.ram or "",
            "colour": variant.colour or "",
            "condition": variant.condition,
        }
    )
