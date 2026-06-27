import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="minify_inventory"
)

cursor = conn.cursor(dictionary=True)