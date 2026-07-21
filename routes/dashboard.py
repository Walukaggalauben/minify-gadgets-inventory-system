<<<<<<< HEAD
# ==========================================
# Dashboard

# ==========================================
from app import app
from db import cursor
from flask import render_template, request, redirect, session, flash
from datetime import datetime
@app.route('/dashboard')
def dashboard():

    # Total Phone Models
    cursor.execute("SELECT COUNT(*) AS total FROM phones")
    totalPhones = cursor.fetchone()

    # Total Stock
    cursor.execute("SELECT IFNULL(SUM(quantity),0) AS stock FROM phones")
    totalStock = cursor.fetchone()

    # Total Sales
    cursor.execute("""
        SELECT IFNULL(SUM(total),0) AS sales
        FROM sales
    """)
    totalSales = cursor.fetchone()

    # Gross Profit
    cursor.execute("""
        SELECT IFNULL(SUM(profit),0) AS profit
        FROM sales
    """)
    totalProfit = cursor.fetchone()

    # Total Expenses
    cursor.execute("""
        SELECT IFNULL(SUM(amount),0) AS expenses
        FROM expenses
    """)
    totalExpenses = cursor.fetchone()

    # Net Profit
    netProfit = {
        "net": float(totalProfit["profit"]) - float(totalExpenses["expenses"])
    }

    # Total Customers
    cursor.execute("""
        SELECT COUNT(*) AS customers
        FROM customers
    """)
    totalCustomers = cursor.fetchone()

    # Best Selling Phone
    cursor.execute("""
        SELECT
            phones.brand,
            phones.model,
            SUM(sales.quantity) AS sold

        FROM sales
        INNER JOIN phones
            ON phones.id = sales.phone_id

        GROUP BY sales.phone_id

        ORDER BY sold DESC

        LIMIT 1
    """)
    bestSelling = cursor.fetchone()

    # Low Stock
    cursor.execute("""
        SELECT
            brand,
            model,
            quantity

        FROM phones

        WHERE quantity <= 2

        ORDER BY quantity ASC
    """)
    lowStock = cursor.fetchall()

    return render_template(
        "dashboard.html",
        totalPhones=totalPhones,
        totalStock=totalStock,
        totalSales=totalSales,
        totalProfit=totalProfit,
        totalExpenses=totalExpenses,
        netProfit=netProfit,
        totalCustomers=totalCustomers,
        bestSelling=bestSelling,
        lowStock=lowStock,
        current_date=datetime.now().strftime("%d %b %Y")
=======
from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect

from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    stats = DashboardService.get_statistics()

    return render_template(

        "dashboard/index.html",

        stats=stats

>>>>>>> main
    )