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
        query = query.filter(
            ProductVariant.quantity > 0,
            ProductVariant.quantity <= ProductVariant.minimum_stock,
        )

    elif status == "out":
        query = query.filter(ProductVariant.quantity <= 0)

    elif status == "in":
        query = query.filter(ProductVariant.quantity > ProductVariant.minimum_stock)

    variants = query.order_by(
        ProductVariant.quantity.asc(), ProductVariant.sku.asc()
    ).all()

    # Load current in-stock physical units once so inventory can show
    # IMEI/serial-level prices without changing ProductVariant pricing.
    variant_ids = [v.id for v in variants]
    in_stock_imeis = (
        IMEI.query.filter(
            IMEI.status == "In Stock",
            IMEI.product_variant_id.in_(variant_ids) if variant_ids else False,
        )
        .order_by(IMEI.product_variant_id.asc(), IMEI.id.asc())
        .all()
    )
    imeis_by_variant = {}
    for unit in in_stock_imeis:
        imeis_by_variant.setdefault(unit.product_variant_id, []).append(unit)

    for variant in variants:
        variant.inventory_units = imeis_by_variant.get(variant.id, [])

    # ==========================================================
    # INVENTORY SUMMARY
    # ==========================================================

    all_variants = ProductVariant.query.all()

    total_variants = len(all_variants)

    total_units = sum(int(v.quantity or 0) for v in all_variants)

    low_stock = sum(
        1
        for v in all_variants
        if 0 < (v.quantity or 0) <= (v.minimum_stock or 0)
    )

    out_of_stock = sum(1 for v in all_variants if (v.quantity or 0) <= 0)

    # Price inventory from physical IMEI units when unit-level prices exist.
    # Remaining quantity falls back to the variant's standard price.
    all_in_stock_imeis = IMEI.query.filter(IMEI.status == "In Stock").all()
    imeis_by_variant_all = {}
    for unit in all_in_stock_imeis:
        imeis_by_variant_all.setdefault(unit.product_variant_id, []).append(unit)

    inventory_cost = 0
    potential_sales = 0
    for v in all_variants:
        units = imeis_by_variant_all.get(v.id, [])
        priced_units = min(len(units), int(v.quantity or 0))
        for unit in units[:priced_units]:
            inventory_cost += unit.buying_price if unit.buying_price is not None else (v.buying_price or 0)
            potential_sales += unit.default_selling_price if unit.default_selling_price is not None else (v.selling_price or 0)
        remaining = max(int(v.quantity or 0) - priced_units, 0)
        inventory_cost += (v.buying_price or 0) * remaining
        potential_sales += (v.selling_price or 0) * remaining

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
