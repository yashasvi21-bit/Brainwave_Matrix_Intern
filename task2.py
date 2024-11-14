import sqlite3

def create_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    name TEXT,
                    quantity INTEGER,
                    price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY,
                    product_id INTEGER,
                    quantity INTEGER,
                    total REAL,
                    sale_date TEXT,
                    FOREIGN KEY(product_id) REFERENCES products(product_id))''')
    conn.commit()
    conn.close()

create_db()

def create_user(username, password):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user is None:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    conn.close()

# Create a new user for testing purposes if it doesn't exist
create_user('admin', 'admin123')

def authenticate_user(username, password):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def add_product(name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

def update_product(product_id, quantity, price):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("UPDATE products SET quantity = ?, price = ? WHERE product_id = ?", (quantity, price, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()

def low_stock_alert(threshold=5):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT name, quantity FROM products WHERE quantity <= ?", (threshold,))
    low_stock_items = c.fetchall()
    conn.close()
    return low_stock_items

import pandas as pd

def generate_sales_report():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT p.name, SUM(s.quantity) as total_sold, SUM(s.total) as total_revenue
                 FROM sales s
                 JOIN products p ON s.product_id = p.product_id
                 GROUP BY p.product_id''')
    sales_data = c.fetchall()
    conn.close()
    
    df = pd.DataFrame(sales_data, columns=['Product', 'Total Sold', 'Total Revenue'])
    return df

import tkinter as tk
from tkinter import messagebox

def create_main_window():
    window = tk.Tk()
    window.title("Inventory Management")

    def on_login():
        username = entry_username.get()
        password = entry_password.get()
        if authenticate_user(username, password):
            messagebox.showinfo("Login", "Login successful!")
            window.quit()
            open_inventory_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")

    tk.Label(window, text="Username").pack(pady=5)
    entry_username = tk.Entry(window)
    entry_username.pack(pady=5)

    tk.Label(window, text="Password").pack(pady=5)
    entry_password = tk.Entry(window, show="*")
    entry_password.pack(pady=5)

    tk.Button(window, text="Login", command=on_login).pack(pady=20)

    window.mainloop()

def open_inventory_window():
    inventory_window = tk.Tk()
    inventory_window.title("Inventory Management System")

    def add_new_product():
        def submit():
            name = entry_name.get()
            quantity = int(entry_quantity.get())
            price = float(entry_price.get())
            add_product(name, quantity, price)
            messagebox.showinfo("Product Added", f"Product '{name}' added to inventory")
            new_product_window.destroy()

        new_product_window = tk.Toplevel(inventory_window)
        new_product_window.title("Add New Product")
        
        tk.Label(new_product_window, text="Product Name").pack(pady=5)
        entry_name = tk.Entry(new_product_window)
        entry_name.pack(pady=5)

        tk.Label(new_product_window, text="Quantity").pack(pady=5)
        entry_quantity = tk.Entry(new_product_window)
        entry_quantity.pack(pady=5)

        tk.Label(new_product_window, text="Price").pack(pady=5)
        entry_price = tk.Entry(new_product_window)
        entry_price.pack(pady=5)

        tk.Button(new_product_window, text="Submit", command=submit).pack(pady=20)

    def show_low_stock():
        low_stock_items = low_stock_alert()
        message = "Low Stock Products:\n"
        for item in low_stock_items:
            message += f"{item[0]}: {item[1]} left\n"
        messagebox.showinfo("Low Stock", message)

    def generate_report():
        report = generate_sales_report()
        messagebox.showinfo("Sales Report", report.to_string())

    tk.Button(inventory_window, text="Add New Product", command=add_new_product).pack(pady=10)
    tk.Button(inventory_window, text="View Low Stock", command=show_low_stock).pack(pady=10)
    tk.Button(inventory_window, text="Generate Sales Report", command=generate_report).pack(pady=10)

    inventory_window.mainloop()

create_main_window()
