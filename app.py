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
    )

    


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

    search = request.args.get("search", "").strip()

    cursor.execute("""
        SELECT
            id,
            brand,
            model,
            color,
            storage,
            ram
        FROM phones
        ORDER BY brand, model
    """)

    phones = cursor.fetchall()

    if search:

        cursor.execute("""
            SELECT
                phone_imei.*,
                phones.brand,
                phones.model,
                phones.color,
                phones.storage,
                phones.ram
            FROM phone_imei
            INNER JOIN phones
            ON phones.id = phone_imei.phone_id
            WHERE phone_imei.imei LIKE %s
            ORDER BY phone_imei.id DESC
        """, ("%" + search + "%",))

    else:

        cursor.execute("""
            SELECT
                phone_imei.*,
                phones.brand,
                phones.model,
                phones.color,
                phones.storage,
                phones.ram
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
        search=search,
        current_date=datetime.now().strftime("%d %b %Y")
    )

# ==========================================
# Save IMEIs
# ==========================================
@app.route("/save_imeis", methods=["POST"])
def save_imeis():

    phone_id = request.form["phone_id"]
    imeis = request.form["imeis"].splitlines()

    imported = 0

    for imei in imeis:

        imei = imei.strip()

        # Skip empty lines
        if imei == "":
            continue

        # Validate IMEI (15 digits)
        if len(imei) != 15 or not imei.isdigit():
            continue

        # Check if IMEI already exists
        cursor.execute(
            "SELECT id FROM phone_imei WHERE imei=%s",
            (imei,)
        )

        existing = cursor.fetchone()

        if existing:
            continue

        cursor.execute(
            """
            INSERT INTO phone_imei
            (
                phone_id,
                imei,
                status
            )
            VALUES
            (
                %s,
                %s,
                'Available'
            )
            """,
            (
                phone_id,
                imei
            )
        )

        imported += 1

    conn.commit()

    print(f"{imported} IMEIs imported successfully.")

    return redirect("/imei_management")

# ==========================================
# Delete IMEI
# ==========================================
@app.route("/delete_imei/<int:id>")
def delete_imei(id):

    cursor.execute(
        "DELETE FROM phone_imei WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect("/imei_management")

# ==========================================
# Edit IMEI Page
# ==========================================
@app.route("/edit_imei/<int:id>")
def edit_imei(id):

    cursor.execute("""
        SELECT
            phone_imei.*,
            phones.brand,
            phones.model
        FROM phone_imei
        INNER JOIN phones
        ON phones.id = phone_imei.phone_id
        WHERE phone_imei.id=%s
    """, (id,))

    imei = cursor.fetchone()

    return render_template(
        "edit_imei.html",
        imei=imei,
        current_date=datetime.now().strftime("%d %b %Y")
    )


# ==========================================
# Update IMEI
# ==========================================
@app.route("/update_imei/<int:id>", methods=["POST"])
def update_imei(id):

    imei_number = request.form["imei"]
    status = request.form["status"]

    # Validate IMEI
    if len(imei_number) != 15 or not imei_number.isdigit():
        return "Invalid IMEI. It must contain exactly 15 digits."

    # Check duplicate (ignore current record)
    cursor.execute("""
        SELECT id
        FROM phone_imei
        WHERE imei=%s
        AND id<>%s
    """, (imei_number, id))

    existing = cursor.fetchone()

    if existing:
        return "This IMEI already exists."

    cursor.execute("""
        UPDATE phone_imei
        SET
            imei=%s,
            status=%s
        WHERE id=%s
    """, (
        imei_number,
        status,
        id
    ))

    conn.commit()

    return redirect("/imei_management")

# ==========================================
# View IMEI
# ==========================================
@app.route("/view_imei/<int:id>")
def view_imei(id):

    cursor.execute("""
        SELECT
            phone_imei.*,
            phones.brand,
            phones.model,
            phones.color,
            phones.phone_condition,
            phones.storage,
            phones.ram,
            phones.buying_price,
            phones.selling_price
        FROM phone_imei
        INNER JOIN phones
        ON phones.id = phone_imei.phone_id
        WHERE phone_imei.id=%s
    """, (id,))

    imei = cursor.fetchone()

    return render_template(
        "view_imei.html",
        imei=imei,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# # ==========================================
# Sales Page
# ==========================================
@app.route("/sales")
def sales():

    imei = request.args.get("imei", "").strip()

    phone = None

    # Load customers
    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_name ASC
    """)

    customers = cursor.fetchall()

    # Search phone by IMEI
    if imei != "":

        cursor.execute("""
            SELECT
                phone_imei.id AS imei_id,
                phone_imei.imei,
                phone_imei.status,

                phones.id AS phone_id,
                phones.brand,
                phones.model,
                phones.color,
                phones.phone_condition,
                phones.storage,
                phones.ram,
                phones.buying_price,
                phones.selling_price

            FROM phone_imei

            INNER JOIN phones

            ON phones.id = phone_imei.phone_id

            WHERE phone_imei.imei=%s

            LIMIT 1
        """, (imei,))

        phone = cursor.fetchone()

    return render_template(
        "sales.html",
        customers=customers,
        phone=phone,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Complete Sale
# ==========================================
@app.route("/complete_sale", methods=["POST"])
def complete_sale():

    phone_id = request.form["phone_id"]
    imei_id = request.form["imei_id"]
    customer_id = request.form["customer_id"]
    sale_price = float(request.form["sale_price"])
    payment_method = request.form["payment_method"]

    # Quantity is always 1 for IMEI sales
    quantity = 1

    # Get buying price
    cursor.execute("""
        SELECT buying_price
        FROM phones
        WHERE id=%s
    """, (phone_id,))

    phone = cursor.fetchone()

    buying_price = float(phone["buying_price"])

    profit = sale_price - buying_price

    total = sale_price

    # Save sale
    cursor.execute("""
        INSERT INTO sales
        (
            phone_id,
            imei_id,
            quantity,
            total,
            profit,
            customer_id,
            sale_price,
            payment_method
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        phone_id,
        imei_id,
        quantity,
        total,
        profit,
        customer_id,
        sale_price,
        payment_method
    ))

    sale_id = cursor.lastrowid

    # Update IMEI status
    cursor.execute("""
        UPDATE phone_imei
        SET
            status='Sold',
            customer_id=%s,
            sale_id=%s
        WHERE id=%s
    """,
    (
        customer_id,
        sale_id,
        imei_id
    ))

    conn.commit()

    return redirect(f"/view_sale/{sale_id}")

# ==========================================
# Sales History
# ==========================================
@app.route("/sales_history")
def sales_history():

    cursor.execute("""
        SELECT
            sales.*,
            customers.customer_name,
            customers.phone,
            phones.brand,
            phones.model,
            phone_imei.imei

        FROM sales

        INNER JOIN customers
            ON customers.id = sales.customer_id

        INNER JOIN phones
            ON phones.id = sales.phone_id

        INNER JOIN phone_imei
            ON phone_imei.id = sales.imei_id

        ORDER BY sales.id DESC
    """)

    sales = cursor.fetchall()

    return render_template(
        "sales_history.html",
        sales=sales,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# View Sale / Receipt
# ==========================================
@app.route("/view_sale/<int:id>")
def view_sale(id):

    cursor.execute("""
        SELECT
            sales.*,
            customers.customer_name,
            customers.phone,
            phones.brand,
            phones.model,
            phones.phone_condition,
            phones.color,
            phones.storage,
            phones.ram,
            phone_imei.imei

        FROM sales

        INNER JOIN customers
            ON customers.id = sales.customer_id

        INNER JOIN phones
            ON phones.id = sales.phone_id

        INNER JOIN phone_imei
            ON phone_imei.id = sales.imei_id

        WHERE sales.id=%s
    """, (id,))

    sale = cursor.fetchone()

    return render_template(
        "view_sale.html",
        sale=sale,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Customers
# ==========================================
@app.route("/customers")
def customers():

    search = request.args.get("search", "")

    if search:

        cursor.execute("""
            SELECT *
            FROM customers
            WHERE customer_name LIKE %s
               OR phone LIKE %s
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%"))

    else:

        cursor.execute("""
            SELECT *
            FROM customers
            ORDER BY id DESC
        """)

    customers = cursor.fetchall()

    return render_template(
        "customers.html",
        customers=customers,
        search=search,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Customer Profile
# ==========================================
@app.route("/customer/<int:id>")
def customer_profile(id):

    # Customer Details
    cursor.execute("""
        SELECT *
        FROM customers
        WHERE id=%s
    """, (id,))

    customer = cursor.fetchone()

    # Purchase History
    cursor.execute("""
        SELECT
            sales.*,
            phones.brand,
            phones.model,
            phones.color,
            phones.storage,
            phones.ram,
            phone_imei.imei

        FROM sales

        INNER JOIN phones
            ON phones.id = sales.phone_id

        INNER JOIN phone_imei
            ON phone_imei.id = sales.imei_id

        WHERE sales.customer_id=%s

        ORDER BY sales.sale_date DESC

    """, (id,))

    purchases = cursor.fetchall()

    return render_template(
        "customer_profile.html",
        customer=customer,
        purchases=purchases,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Edit Customer
# ==========================================
@app.route("/edit_customer/<int:id>")
def edit_customer(id):

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE id=%s
    """, (id,))

    customer = cursor.fetchone()

    return render_template(
        "edit_customer.html",
        customer=customer,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Update Customer
# ==========================================
@app.route("/update_customer/<int:id>", methods=["POST"])
def update_customer(id):

    customer_name = request.form["customer_name"]
    phone = request.form["phone"]

    cursor.execute("""
        UPDATE customers
        SET
            customer_name=%s,
            phone=%s
        WHERE id=%s
    """,
    (
        customer_name,
        phone,
        id
    ))

    conn.commit()

    return redirect("/customers")

# ==========================================
# Delete Customer
# ==========================================
@app.route("/delete_customer/<int:id>")
def delete_customer(id):

    cursor.execute("""
        DELETE FROM customers
        WHERE id=%s
    """, (id,))

    conn.commit()

    return redirect("/customers")                    
# ==========================================
# Expenses
# ==========================================
@app.route("/expenses")
def expenses():

    search = request.args.get("search", "")

    if search:

        cursor.execute("""
            SELECT *
            FROM expenses
            WHERE expense_name LIKE %s
            ORDER BY expense_date DESC
        """, (f"%{search}%",))

    else:

        cursor.execute("""
            SELECT *
            FROM expenses
            ORDER BY expense_date DESC
        """)

    expenses = cursor.fetchall()

    return render_template(
        "expenses.html",
        expenses=expenses,
        search=search,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Add Expense
# ==========================================
@app.route("/add_expense")
def add_expense():

    return render_template(
        "add_expense.html",
        current_date=datetime.now().strftime("%d %b %Y")
    ) 
    
# ==========================================
# Save Expense
# ==========================================
@app.route("/save_expense", methods=["POST"])
def save_expense():

    expense_name = request.form["expense_name"]
    amount = request.form["amount"]

    cursor.execute("""
        INSERT INTO expenses
        (
            expense_name,
            amount
        )
        VALUES
        (%s,%s)
    """,
    (
        expense_name,
        amount
    ))

    conn.commit()

    return redirect("/expenses")  

# ==========================================
# Edit Expense
# ==========================================
@app.route("/edit_expense/<int:id>")
def edit_expense(id):

    cursor.execute(
        "SELECT * FROM expenses WHERE id=%s",
        (id,)
    )

    expense = cursor.fetchone()

    return render_template(
        "edit_expense.html",
        expense=expense,
        current_date=datetime.now().strftime("%d %b %Y")
    ) 
    
# ==========================================
# Update Expense
# ==========================================
@app.route("/update_expense/<int:id>", methods=["POST"])
def update_expense(id):

    expense_name = request.form["expense_name"]
    amount = request.form["amount"]

    cursor.execute("""
        UPDATE expenses
        SET
            expense_name=%s,
            amount=%s
        WHERE id=%s
    """,
    (
        expense_name,
        amount,
        id
    ))

    conn.commit()

    return redirect("/expenses")

# ==========================================
# Delete Expense
# ==========================================
@app.route("/delete_expense/<int:id>")
def delete_expense(id):

    cursor.execute(
        "DELETE FROM expenses WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect("/expenses")

# ==========================================
# Suppliers
# ==========================================
@app.route("/suppliers")
def suppliers():

    search = request.args.get("search", "")

    if search:

        cursor.execute("""
            SELECT *
            FROM suppliers
            WHERE supplier_name LIKE %s
               OR phone LIKE %s
            ORDER BY supplier_name
        """,
        (
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM suppliers
            ORDER BY supplier_name
        """)

    suppliers = cursor.fetchall()

    return render_template(
        "suppliers.html",
        suppliers=suppliers,
        search=search,
        current_date=datetime.now().strftime("%d %b %Y")
    )

# ==========================================
# Add Supplier
# ==========================================
@app.route("/add_supplier")
def add_supplier():

    return render_template(
        "add_supplier.html",
        current_date=datetime.now().strftime("%d %b %Y")
    )


# ==========================================
# Save Supplier
# ==========================================
@app.route("/save_supplier", methods=["POST"])
def save_supplier():

    supplier_name = request.form["supplier_name"]
    contact_person = request.form["contact_person"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]

    cursor.execute("""
        INSERT INTO suppliers
        (
            supplier_name,
            contact_person,
            phone,
            email,
            address
        )
        VALUES
        (%s,%s,%s,%s,%s)
    """,
    (
        supplier_name,
        contact_person,
        phone,
        email,
        address
    ))

    conn.commit()

    return redirect("/suppliers")

# ==========================================
# Purchases
# ==========================================
@app.route("/purchases")
def purchases():

    cursor.execute("""
        SELECT
            purchases.*,
            suppliers.supplier_name,
            phones.brand,
            phones.model

        FROM purchases

        INNER JOIN suppliers
            ON suppliers.id = purchases.supplier_id

        INNER JOIN phones
            ON phones.id = purchases.phone_id

        ORDER BY purchases.purchase_date DESC
    """)

    purchases = cursor.fetchall()

    return render_template(
        "purchases.html",
        purchases=purchases,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Add Purchase
# ==========================================
@app.route("/add_purchase")
def add_purchase():

    cursor.execute("""
        SELECT *
        FROM suppliers
        ORDER BY supplier_name
    """)
    suppliers = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM phones
        ORDER BY brand, model
    """)
    phones = cursor.fetchall()

    return render_template(
        "add_purchase.html",
        suppliers=suppliers,
        phones=phones,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Purchase Headers
# ==========================================
@app.route("/purchase_headers")
def purchase_headers():

    search = request.args.get("search", "")

    if search:

        cursor.execute("""
            SELECT
                purchase_headers.*,
                suppliers.supplier_name

            FROM purchase_headers

            INNER JOIN suppliers
                ON suppliers.id = purchase_headers.supplier_id

            WHERE purchase_headers.purchase_no LIKE %s
               OR suppliers.supplier_name LIKE %s

            ORDER BY purchase_headers.id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                purchase_headers.*,
                suppliers.supplier_name

            FROM purchase_headers

            INNER JOIN suppliers
                ON suppliers.id = purchase_headers.supplier_id

            ORDER BY purchase_headers.id DESC
        """)

    purchases = cursor.fetchall()

    return render_template(
        "purchase_headers.html",
        purchases=purchases,
        search=search,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# New Purchase Header
# ==========================================
@app.route("/new_purchase")
def new_purchase():

    cursor.execute("""
        SELECT *
        FROM suppliers
        ORDER BY supplier_name
    """)

    suppliers = cursor.fetchall()

    return render_template(
        "new_purchase.html",
        suppliers=suppliers,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Save Purchase Header
# ==========================================
@app.route("/save_purchase_header", methods=["POST"])
def save_purchase_header():

    supplier_id = request.form["supplier_id"]

    purchase_type = request.form["purchase_type"]

    payment_status = request.form["payment_status"]

    invoice_no = request.form["invoice_no"]

    notes = request.form["notes"]

    if purchase_type == "Local":

        shipment_status = "Received"

    else:

        shipment_status = "Pending Shipment"

    cursor.execute("""

        SELECT COUNT(*) AS total

        FROM purchase_headers

    """)

    total = cursor.fetchone()["total"] + 1

    purchase_no = f"PUR-{datetime.now().year}-{total:05d}"

    cursor.execute("""

        INSERT INTO purchase_headers(

            purchase_no,

            supplier_id,

            purchase_type,

            payment_status,

            shipment_status,

            invoice_no,

            notes

        )

        VALUES(

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s

        )

    """,(

        purchase_no,

        supplier_id,

        purchase_type,

        payment_status,

        shipment_status,

        invoice_no,

        notes

    ))

    conn.commit()

    purchase_id = cursor.lastrowid

    return redirect(f"/purchase/{purchase_id}")

# ==========================================
# Purchase Details
# ==========================================
@app.route("/purchase/<int:id>")
def purchase_details(id):

    # Purchase Header
    cursor.execute("""
        SELECT
            purchase_headers.*,
            suppliers.supplier_name
        FROM purchase_headers
        INNER JOIN suppliers
            ON suppliers.id = purchase_headers.supplier_id
        WHERE purchase_headers.id=%s
    """, (id,))

    purchase = cursor.fetchone()

    # Phone Variants
    cursor.execute("""
        SELECT *
        FROM phones
        ORDER BY brand, model, storage
    """)

    phones = cursor.fetchall()

    # Purchase Items
    cursor.execute("""
        SELECT
            purchase_items.*,
            phones.brand,
            phones.model,
            phones.color,
            phones.storage,
            phones.ram

        FROM purchase_items

        INNER JOIN phones
            ON phones.id = purchase_items.phone_id

        WHERE purchase_header_id=%s

        ORDER BY purchase_items.id
    """, (id,))

    items = cursor.fetchall()

    return render_template(
        "purchase_details.html",
        purchase=purchase,
        phones=phones,
        items=items,
        current_date=datetime.now().strftime("%d %b %Y")
    )
    
# ==========================================
# Add Purchase Item
# ==========================================
@app.route("/add_purchase_item", methods=["POST"])
def add_purchase_item():

    purchase_header_id = request.form["purchase_header_id"]
    phone_id = request.form["phone_id"]
    quantity = request.form["quantity"]
    buying_price = request.form["buying_price"]
    target_price = request.form["target_price"]
    minimum_price = request.form["minimum_price"]

    cursor.execute("""
        INSERT INTO purchase_items
        (
            purchase_header_id,
            phone_id,
            quantity,
            buying_price,
            target_selling_price,
            minimum_selling_price
        )
        VALUES
        (%s,%s,%s,%s,%s,%s)
    """,
    (
        purchase_header_id,
        phone_id,
        quantity,
        buying_price,
        target_price,
        minimum_price
    ))

    conn.commit()

    return redirect(f"/purchase/{purchase_header_id}")

# ==========================================
# Get Phone Details (AJAX)
# ==========================================
@app.route("/get_phone/<int:id>")
def get_phone(id):

    cursor.execute("""
        SELECT
            buying_price,
            selling_price
        FROM phones
        WHERE id=%s
    """, (id,))

    phone = cursor.fetchone()

    if phone:

        return {
            "buying_price": float(phone["buying_price"]),
            "selling_price": float(phone["selling_price"])
        }

    return {}    
    
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )