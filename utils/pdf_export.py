from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from utils.timezone import application_now

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def _money(value):
    return f"UGX {float(value or 0):,.0f}"


def create_sale_invoice_pdf(sale, company, settings):
    """Create a customer-shareable PDF of the existing sale invoice."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(8.5 * inch, 11 * inch), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title = styles["Title"]
    title.textColor = colors.HexColor("#198754")
    elements = [Paragraph(escape(company.business_name or "MINIFY GADGETS"), title)]
    elements.append(Paragraph("TAX INVOICE", styles["Heading2"]))
    elements.append(Paragraph(f"Invoice: <b>{escape(sale.invoice_number)}</b> &nbsp;&nbsp; Date: {sale.sale_date.strftime('%d %B %Y %I:%M %p')}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Customer: <b>{escape(sale.customer_name or 'Walk-in Customer')}</b>", styles["Normal"]))
    if sale.customer_phone:
        elements.append(Paragraph(f"Phone: {escape(sale.customer_phone)}", styles["Normal"]))
    elements.append(Spacer(1, 15))
    data = [["Product", "Qty", "Unit Price", "Total"]]
    for item in sale.items:
        name = f"{item.product_variant.product.brand.name} {item.product_variant.product.name}"
        details = " / ".join(filter(None, [item.product_variant.storage, item.product_variant.ram, item.product_variant.colour]))
        if details:
            name += f"\n{details}"
        data.append([Paragraph(escape(name).replace("\n", "<br/>"), styles["Normal"]), str(item.quantity), _money(item.selling_price), _money(item.total)])
    data.append(["", "", "GRAND TOTAL", _money(sale.total_amount)])
    table = Table(data, colWidths=[3.8*inch, .6*inch, 1.15*inch, 1.15*inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#198754")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("GRID", (0,0), (-1,-1), .5, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ALIGN", (1,1), (-1,-1), "RIGHT"), ("FONTNAME", (2,-1), (-1,-1), "Helvetica-Bold"), ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f1f8f6"))]))
    elements.extend([table, Spacer(1, 18), Paragraph(f"Payment: {sale.payment_method or 'Cash'}", styles["Normal"])])
    elements.append(Paragraph(f"Amount Paid: {_money(sale.amount_paid)} &nbsp;&nbsp; Balance Due: {_money(sale.balance_due)}", styles["Normal"]))
    if settings.receipt_footer:
        elements.extend([Spacer(1, 15), Paragraph(settings.receipt_footer, styles["Normal"])])
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Thank you for shopping with MINIFY GADGETS.", styles["Normal"]))
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_payment_receipt_pdf(payment, sale, company, settings, net_payment_amount=None):
    """Create a customer-shareable PDF for one actual payment receipt."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(8.5 * inch, 11 * inch), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title = styles["Title"]
    title.textColor = colors.HexColor("#00695c")
    net_amount = payment.amount if net_payment_amount is None else net_payment_amount
    elements = [Paragraph(company.business_name or "MINIFY GADGETS", title), Paragraph("PAYMENT RECEIPT", styles["Heading2"])]
    elements.append(Paragraph(f"Receipt No: <b>{payment.receipt_number}</b> &nbsp;&nbsp; Invoice: <b>{sale.invoice_number}</b>", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Customer: <b>{sale.customer_name or 'Walk-in Customer'}</b>", styles["Normal"]))
    if sale.customer_phone:
        elements.append(Paragraph(f"Phone: {sale.customer_phone}", styles["Normal"]))
    elements.append(Spacer(1, 15))
    currency = payment.currency.symbol or payment.currency.code if payment.currency else "UGX"
    rows = [["Payment Detail", "Value"], ["Receipt Date", payment.payment_date.strftime('%d/%m/%Y %H:%M') if payment.payment_date else "-"], ["Payment Method", payment.payment_method or "-"], ["Amount Received", f"{currency} {float(net_amount / (payment.exchange_rate or 1)):,.2f}"], ["UGX Equivalent", _money(net_amount)], ["Exchange Rate", f"{float(payment.exchange_rate or 1):,.8f}"], ["Remaining Balance", _money(sale.balance_due)]]
    table = Table(rows, colWidths=[2.6*inch, 4.1*inch])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#00695c")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("GRID", (0,0), (-1,-1), .5, colors.grey), ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"), ("ALIGN", (1,1), (1,-1), "RIGHT")]))
    elements.extend([table, Spacer(1, 18)])
    if payment.reference:
        elements.append(Paragraph(f"Reference: {payment.reference}", styles["Normal"]))
    if payment.notes:
        elements.append(Paragraph(f"Notes: {payment.notes}", styles["Normal"]))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(settings.receipt_footer or "Thank you for your payment.", styles["Normal"]))
    doc.build(elements)
    buffer.seek(0)
    return buffer


class PDFExporter:

    @staticmethod
    def create_table_pdf(title, headers, rows, summary=None):
        """
        Generic PDF Generator
        """

        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=(11 * inch, 8.5 * inch))

        styles = getSampleStyleSheet()

        title_style = styles["Heading1"]
        title_style.alignment = TA_CENTER

        normal = styles["Normal"]

        elements = []

        elements.append(Paragraph("<b>MINIFY GADGETS</b>", title_style))

        elements.append(Paragraph("Inventory Management System", styles["Heading2"]))

        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))

        elements.append(
            Paragraph(
                f"Generated: {application_now().strftime('%d %B %Y %I:%M %p')}", normal
            )
        )

        elements.append(Spacer(1, 15))

        data = [headers]

        for row in rows:
            data.append(row)

        table = Table(data, repeatRows=1)

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#0f766e"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.beige,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        10,
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                ]
            )
        )

        elements.append(table)

        if summary:

            elements.append(Spacer(1, 20))

            elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))

            for key, value in summary.items():

                elements.append(
                    Paragraph(f"<b>{key.replace('_',' ').title()}:</b> {value}", normal)
                )

        doc.build(elements)

        pdf = buffer.getvalue()

        buffer.close()

        return pdf

    # ==========================================================
    # SALES REPORT
    # ==========================================================

    @staticmethod
    def sales_report(sales, summary):

        headers = [
            "Invoice",
            "Customer",
            "Date",
            "Total",
            "Profit",
        ]

        rows = []

        for sale in sales:

            rows.append(
                [
                    sale.invoice_number,
                    sale.customer_name or "-",
                    sale.sale_date.strftime("%d/%m/%Y"),
                    f"{float(sale.total_amount):,.2f}",
                    f"{float(sale.profit):,.2f}",
                ]
            )

        return PDFExporter.create_table_pdf(
            title="Sales Report",
            headers=headers,
            rows=rows,
            summary={
                "Invoice Count": summary["invoice_count"],
                "Total Sales": f"{summary['total_sales']:,.2f}",
                "Total Profit": f"{summary['total_profit']:,.2f}",
            },
        )
        # ==========================================================

    # PURCHASE REPORT
    # ==========================================================

    @staticmethod
    def purchase_report(purchases, summary):

        headers = [
            "Purchase No",
            "Supplier",
            "Date",
            "Status",
            "Total",
        ]

        rows = []

        for purchase in purchases:

            rows.append(
                [
                    purchase.purchase_number,
                    purchase.supplier.name if purchase.supplier else "-",
                    purchase.purchase_date.strftime("%d/%m/%Y"),
                    purchase.status,
                    f"{float(purchase.total_amount):,.2f}",
                ]
            )

        return PDFExporter.create_table_pdf(
            title="Purchase Report",
            headers=headers,
            rows=rows,
            summary={
                "Purchase Count": summary["count"],
                "Total Purchases": f"{summary['total']:,.2f}",
            },
        )

        # =============================================

    # INVENTORY REPORT
    # =============================================

    @staticmethod
    def inventory_report(variants, summary):

        headers = [
            "Product",
            "SKU",
            "Colour",
            "Storage",
            "Buying",
            "Selling",
            "Stock",
            "Cost Value",
            "Selling Value",
            "Profit",
        ]

        rows = []

        for item in variants:

            quantity = item.quantity or 0

            buying_price = float(item.buying_price or 0)

            selling_price = float(item.selling_price or 0)

            cost_value = buying_price * quantity

            selling_value = selling_price * quantity

            expected_profit = selling_value - cost_value

            rows.append(
                [
                    item.product.name if item.product else "",
                    item.sku or "-",
                    item.colour or "-",
                    item.storage or "-",
                    f"{buying_price:,.2f}",
                    f"{selling_price:,.2f}",
                    quantity,
                    f"{cost_value:,.2f}",
                    f"{selling_value:,.2f}",
                    f"{expected_profit:,.2f}",
                ]
            )

        return PDFExporter.create_table_pdf(
            title="Inventory Report",
            headers=headers,
            rows=rows,
            summary={
                "Total Variants": summary.get("products", len(variants)),
                "Total Stock": summary.get(
                    "stock", sum(v.quantity or 0 for v in variants)
                ),
                "Inventory Cost Value": (f"{summary.get('cost_value', 0):,.2f}"),
                "Potential Selling Value": (f"{summary.get('selling_value', 0):,.2f}"),
                "Expected Profit": (f"{summary.get('expected_profit', 0):,.2f}"),
            },
        )
        # ==========================================================

    # PROFIT REPORT
    # ==========================================================

    @staticmethod
    def profit_report(sales, summary):

        headers = [
            "Invoice",
            "Customer",
            "Date",
            "Sales",
            "Profit",
        ]

        rows = []

        for sale in sales:

            rows.append(
                [
                    sale.invoice_number,
                    sale.customer_name or "-",
                    sale.sale_date.strftime("%d/%m/%Y"),
                    f"{float(sale.total_amount):,.2f}",
                    f"{float(sale.profit):,.2f}",
                ]
            )

        return PDFExporter.create_table_pdf(
            title="Profit Report",
            headers=headers,
            rows=rows,
            summary={
                "Sales": summary["sales"],
                "Total Profit": f"{summary['profit']:,.2f}",
                "Average Profit": f"{summary['average_profit']:,.2f}",
            },
        )

    # ==========================================================
    # IMEI REPORT
    # ==========================================================

    @staticmethod
    def imei_report(imeis, summary=None):

        headers = [
            "IMEI",
            "Product",
            "SKU",
            "Storage",
            "Colour",
            "Status",
            "Supplier",
            "Purchase",
            "Buying Cost",
            "Customer",
            "Sale",
            "Selling Price",
            "Profit",
        ]

        rows = []

        for item in imeis:

            variant = item.product_variant

            product = variant.product.name if variant and variant.product else "-"

            rows.append(
                [
                    item.imei,
                    product,
                    variant.sku if variant else "-",
                    variant.storage if variant else "-",
                    variant.colour if variant else "-",
                    item.status,
                    item.supplier.name if item.supplier else "-",
                    item.purchase_number or "-",
                    str(item.buying_price or 0),
                    (
                        item.sale_items[0].sale.customer_name
                        if item.sale_items and item.sale_items[0].sale
                        else "-"
                    ),
                    (
                        item.sale_items[0].sale.invoice_number
                        if item.sale_items and item.sale_items[0].sale
                        else "-"
                    ),
                    (
                        str(item.sale_items[0].selling_price or 0)
                        if item.sale_items
                        else "-"
                    ),
                    str(item.sale_items[0].profit or 0) if item.sale_items else "-",
                ]
            )

        if summary is None:

            summary = {
                "Total IMEIs": len(imeis),
                "In Stock": len([i for i in imeis if i.status == "In Stock"]),
                "Sold": len([i for i in imeis if i.status == "Sold"]),
            }

        return PDFExporter.create_table_pdf(
            title="IMEI Report",
            headers=headers,
            rows=rows,
            summary=summary,
        )
        # ==========================================================

    # LOW STOCK REPORT
    # ==========================================================

    @staticmethod
    def low_stock_report(variants, summary=None):

        headers = [
            "Product",
            "SKU",
            "Colour",
            "Storage",
            "Current Stock",
            "Minimum Stock",
        ]

        rows = []

        for item in variants:

            rows.append(
                [
                    item.product.name if item.product else "-",
                    item.sku,
                    item.colour or "-",
                    item.storage or "-",
                    item.quantity,
                    item.minimum_stock,
                ]
            )

        if summary is None:

            summary = {"Low Stock Products": len(variants)}

        return PDFExporter.create_table_pdf(
            title="Low Stock Report",
            headers=headers,
            rows=rows,
            summary=summary,
        )
