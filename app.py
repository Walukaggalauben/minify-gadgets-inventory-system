from flask import Flask, render_template, request, redirect
from db import cursor, conn
from datetime import datetime

app = Flask(__name__)


# ==========================================
# Login
# ==========================================
@app.route('/')
def login():
    return render_template("login.html")


# ==========================================
# Dashboard
# ==========================================
@app.route('/dashboard')
def dashboard():

    try:

        cursor.execute("SELECT COUNT(*) AS total FROM phones")
        totalPhones = cursor.fetchone()

        cursor.execute("SELECT IFNULL(SUM(quantity),0) AS stock FROM phones")
        totalStock = cursor.fetchone()

        cursor.execute("""
            SELECT IFNULL(SUM(selling_price * quantity),0) AS sales
            FROM phones
        """)
        totalSales = cursor.fetchone()

        cursor.execute("""
            SELECT IFNULL(SUM((selling_price-buying_price)*quantity),0) AS profit
            FROM phones
        """)
        totalProfit = cursor.fetchone()

        return render_template(
            "dashboard.html",
            totalPhones=totalPhones,
            totalStock=totalStock,
            totalSales=totalSales,
            totalProfit=totalProfit,
            current_date=datetime.now().strftime("%d %b %Y")
        )

    except Exception as e:
        return f"Database Error: {e}"


# ==========================================
# Inventory
# ==========================================
@app.route('/inventory')
def inventory():

    cursor.execute("""
        SELECT *
        FROM phones
        ORDER BY id DESC
    """)

    phones = cursor.fetchall()

    return render_template(
        "inventory.html",
        phones=phones,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
    
# ==========================
# Phone Details
# ==========================
@app.route('/phone/<int:id>')
def phone_details(id):

    cursor.execute(
        "SELECT * FROM phones WHERE id=%s",
        (id,)
    )

    phone = cursor.fetchone()

    return render_template(
        "phone_details.html",
        phone=phone,
        current_date=datetime.now().strftime("%d %b %Y")
    )    


# ==========================================
# Add Phone Page
# ==========================================
@app.route('/add_phone')
def add_phone():

    return render_template(
        "add_phone.html",
        current_date=datetime.now().strftime("%d %b %Y")
    )


# ==========================================
# Save Phone
# ==========================================
@app.route('/save_phone', methods=["POST"])
def save_phone():

    brand = request.form["brand"]
    model = request.form["model"]
    color = request.form["color"]
    phone_condition = request.form["condition"]
    storage = request.form["storage"]
    ram = request.form["ram"]
    buying_price = request.form["buying_price"]
    selling_price = request.form["selling_price"]
    quantity = request.form["quantity"]
    

    cursor.execute("""
    INSERT INTO phones
    (
        brand,
        model,
        color,
        phone_condition,
        storage,
        ram,
        buying_price,
        selling_price,
        quantity
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s)
""",
(
    brand,
    model,
    color,
    phone_condition,
    storage,
    ram,
    buying_price,
    selling_price,
    quantity
))

    conn.commit()

    return redirect("/inventory")


# ==========================================
# Edit Phone Page
# ==========================================
@app.route('/edit_phone/<int:id>')
def edit_phone(id):

    cursor.execute(
        "SELECT * FROM phones WHERE id=%s",
        (id,)
    )

    phone = cursor.fetchone()

    return render_template(
        "edit_phone.html",
        phone=phone,
        current_date=datetime.now().strftime("%d %b %Y")
    )


# ==========================================
# Update Phone
# ==========================================
@app.route('/update_phone/<int:id>', methods=["POST"])
def update_phone(id):

    brand = request.form["brand"]
    model = request.form["model"]
    color = request.form["color"]
    phone_condition = request.form["condition"]
    storage = request.form["storage"]
    ram = request.form["ram"]
    buying_price = request.form["buying_price"]
    selling_price = request.form["selling_price"]
    quantity = request.form["quantity"]
    

    cursor.execute("""
    UPDATE phones
    SET
        brand=%s,
        model=%s,
        color=%s,
        phone_condition=%s,
        storage=%s,
        ram=%s,
        buying_price=%s,
        selling_price=%s,
        quantity=%s
    WHERE id=%s
""",
(
    brand,
    model,
    color,
    phone_condition,
    storage,
    ram,
    buying_price,
    selling_price,
    quantity,
    id
))

    conn.commit()

    return redirect("/inventory")


# ==========================================
# Delete Phone
# ==========================================
@app.route('/delete_phone/<int:id>')
def delete_phone(id):

    cursor.execute(
        "DELETE FROM phones WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect("/inventory")


# ==========================================
# Run Flask
# ==========================================

# ==========================================
# IMEI Management
# ==========================================
@app.route("/imei_management")
def imei_management():

    cursor.execute("""
        SELECT id, brand, model
        FROM phones
        ORDER BY brand, model
    """)

    phones = cursor.fetchall()

    cursor.execute("""
        SELECT
            phone_imei.*,
            phones.brand,
            phones.model
        FROM phone_imei
        INNER JOIN phones
        ON phones.id = phone_imei.phone_id
        ORDER BY phone_imei.id DESC
    """)

    imeis = cursor.fetchall()

    return render_template(
        "imei_management.html",
        phones=phones,
        imeis=imeis,
        current_date=datetime.now().strftime("%d %b %Y")
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )