from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
)



from services.report_service import ReportService

# We'll create this in the next step
try:
    from utils.pdf_export import PDFExporter
except ImportError:
    PDFExporter = None

try:
    from utils.excel_export import ExcelExporter
except ImportError:
    ExcelExporter = None

report_bp = Blueprint(
    "report",
    __name__,
    url_prefix="/reports"
)


# ==========================================================
# REPORTS DASHBOARD
# ==========================================================

@report_bp.route("/")
def index():

    dashboard = ReportService.dashboard_summary()

    return render_template(
        "reports/index.html",
        dashboard=dashboard
    )


# ==========================================================
# SALES REPORT
# ==========================================================

@report_bp.route("/sales")
def sales_report():

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    sales, summary = ReportService.sales_report(
        start_date,
        end_date
    )

    return render_template(
        "reports/sales_report.html",
        sales=sales,
        summary=summary,
        start_date=start_date,
        end_date=end_date,
    )


# ==========================================================
# SALES REPORT PDF
# ==========================================================

@report_bp.route("/sales/pdf")
def sales_report_pdf():

    if PDFExporter is None:
        flash("PDF exporter has not been configured.", "warning")
        return redirect(url_for("report.sales_report"))

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    sales, summary = ReportService.sales_report(
        start_date,
        end_date
    )

    pdf = PDFExporter.sales_report(
        sales,
        summary,
        
    )

    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="sales_report.pdf",
        mimetype="application/pdf",
    )

# ==========================================================
# SALES REPORT EXCEL
# ==========================================================

@report_bp.route("/sales/excel")
def sales_report_excel():

    if ExcelExporter is None:
        flash("Excel exporter has not been configured.", "warning")
        return redirect(url_for("report.sales_report"))

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    sales, summary = ReportService.sales_report(
        start_date,
        end_date,
    )

    excel = ExcelExporter.sales_report(
        sales,
    )

    return send_file(
        excel,
        as_attachment=True,
        download_name="sales_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ==========================================================
# INVENTORY REPORT
# ==========================================================

@report_bp.route("/inventory")
def inventory_report():

    products, summary = ReportService.inventory_report()

    return render_template(
        "reports/inventory_report.html",
        products=products,
        summary=summary,
    )

# ==========================================================
# INVENTORY REPORT PDF
# ==========================================================

@report_bp.route("/inventory/pdf")
def inventory_report_pdf():

    products, summary = ReportService.inventory_report()

    pdf = PDFExporter.inventory_report(
        products,
        summary,
    )

    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="inventory_report.pdf",
        mimetype="application/pdf",
    )
    
# ==========================================================
# INVENTORY REPORT EXCEL
# ==========================================================

@report_bp.route("/inventory/excel")
def inventory_report_excel():

    if ExcelExporter is None:
        flash("Excel exporter has not been configured.", "warning")
        return redirect(url_for("report.inventory_report"))

    products, summary = ReportService.inventory_report()

    excel = ExcelExporter.inventory_report(
        products,
    )

    return send_file(
        excel,
        as_attachment=True,
        download_name="inventory_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )    

# ==========================================================
# PURCHASE REPORT
# ==========================================================

@report_bp.route("/purchases")
def purchase_report():

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    purchases, summary = ReportService.purchase_report(
        start_date,
        end_date,
    )

    return render_template(
        "reports/purchase_report.html",
        purchases=purchases,
        summary=summary,
        start_date=start_date,
        end_date=end_date,
    )
    
@report_bp.route("/purchases/pdf")
def purchase_report_pdf():

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    purchases, summary = ReportService.purchase_report(
        start_date,
        end_date,
    )

    pdf = PDFExporter.purchase_report(
        purchases,
        summary,
    )

    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="purchase_report.pdf",
        mimetype="application/pdf",
    ) 
    
# ==========================================================
# PURCHASE REPORT EXCEL
# ==========================================================

@report_bp.route("/purchases/excel")
def purchase_report_excel():

    if ExcelExporter is None:
        flash("Excel exporter has not been configured.", "warning")
        return redirect(url_for("report.purchase_report"))

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    purchases, summary = ReportService.purchase_report(
        start_date,
        end_date,
    )

    excel = ExcelExporter.purchase_report(
        purchases,
    )

    return send_file(
        excel,
        as_attachment=True,
        download_name="purchase_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )       


# ==========================================================
# PROFIT REPORT
# ==========================================================

@report_bp.route("/profit")
def profit_report():

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    sales, summary = ReportService.profit_report(
        start_date,
        end_date,
    )

    return render_template(
        "reports/profit_report.html",
        sales=sales,
        summary=summary,
        start_date=start_date,
        end_date=end_date,
    )

# ==========================================================
# PROFIT REPORT PDF
# ==========================================================

@report_bp.route("/profit/pdf")
def profit_report_pdf():

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    sales, summary = ReportService.profit_report(
        start_date,
        end_date,
    )

    pdf = PDFExporter.profit_report(
        sales,
        summary,
    )

    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="profit_report.pdf",
        mimetype="application/pdf",
    )
    
# ==========================================================
# PROFIT REPORT EXCEL
# ==========================================================

@report_bp.route("/profit/excel")
def profit_report_excel():

    if ExcelExporter is None:
        flash("Excel exporter has not been configured.", "warning")
        return redirect(url_for("report.profit_report"))

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    sales, summary = ReportService.profit_report(
        start_date,
        end_date,
    )

    excel = ExcelExporter.profit_report(
        sales,
    )

    return send_file(
        excel,
        as_attachment=True,
        download_name="profit_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )    
    

# ==========================================================
# IMEI REPORT
# ==========================================================

@report_bp.route("/imei")
def imei_report():

    imeis = ReportService.imei_report()

    return render_template(
        "reports/imei_report.html",
        imeis=imeis,
    )

# ==========================================================
# IMEI REPORT PDF
# ==========================================================

@report_bp.route("/imei/pdf")
def imei_report_pdf():

    imeis = ReportService.imei_report()

    pdf = PDFExporter.imei_report(
        imeis,
    )

    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="imei_report.pdf",
        mimetype="application/pdf",
    )
    
# ==========================================================
# IMEI REPORT EXCEL
# ==========================================================

@report_bp.route("/imei/excel")
def imei_report_excel():

    if ExcelExporter is None:
        flash("Excel exporter has not been configured.", "warning")
        return redirect(url_for("report.imei_report"))

    imeis = ReportService.imei_report()

    excel = ExcelExporter.imei_report(
        imeis,
    )

    return send_file(
        excel,
        as_attachment=True,
        download_name="imei_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )    

# ==========================================================
# LOW STOCK REPORT
# ==========================================================

@report_bp.route("/low-stock")
def low_stock_report():

    products = ReportService.low_stock_report()

    return render_template(
        "reports/low_stock_report.html",
        products=products,
    )
    
# ==========================================================
# LOW STOCK REPORT PDF
# ==========================================================

@report_bp.route("/low-stock/pdf")
def low_stock_report_pdf():

    products = ReportService.low_stock_report()

    pdf = PDFExporter.low_stock_report(
        products,
    )

    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="low_stock_report.pdf",
        mimetype="application/pdf",
    )
    
# ==========================================================
# LOW STOCK REPORT EXCEL
# ==========================================================

@report_bp.route("/low-stock/excel")
def low_stock_report_excel():

    if ExcelExporter is None:
        flash("Excel exporter has not been configured.", "warning")
        return redirect(url_for("report.low_stock_report"))

    products = ReportService.low_stock_report()

    excel = ExcelExporter.low_stock_report(
        products,
    )

    return send_file(
        excel,
        as_attachment=True,
        download_name="low_stock_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )        

@report_bp.route("/expenses")
def expense_report():
    from models.expense import Expense
    expenses = Expense.query.order_by(Expense.expense_date.desc(), Expense.id.desc()).all()
    total = sum(float(e.amount or 0) for e in expenses)
    return render_template("reports/expense_report.html", expenses=expenses, total=total)
