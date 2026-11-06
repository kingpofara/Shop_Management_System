# ==========================================
# SHOP MANAGEMENT SYSTEM
# ==========================================
# Shop Management System - Version 1.1
import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()


# ==========================================
# DATABASE CONNECTION
# ==========================================

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT"))
)


# ==========================================
# INVENTORY FUNCTIONS
# ==========================================

def display_products():
    cursor = connection.cursor()

    try:
        query = "SELECT * FROM products ORDER BY product_id"
        cursor.execute(query)
        products = cursor.fetchall()

        if not products:
            print("No products found.")
            return

        print("\n========== PRODUCT INVENTORY ==========")

        for product in products:
            print(f"Product ID: {product[0]}")
            print(f"Product Name: {product[1]}")
            print(f"Available Stock: {product[2]}")
            print(f"Unit Price: GH₵{product[3]:,.2f}")
            print("-" * 40)

    finally:
        cursor.close()


def low_stock_report(threshold):
    cursor = connection.cursor()

    try:
        if threshold <= 0:
            print("Quantity should be a positive number.")
            return

        query = """
            SELECT product_id, product_name, quantity
            FROM products
            WHERE quantity < %s
            ORDER BY quantity ASC
        """

        cursor.execute(query, (threshold,))
        low_stock = cursor.fetchall()

        if not low_stock:
            print("No products are below the specified stock threshold.")
            return

        print("\n========== LOW STOCK REPORT ==========")

        for row in low_stock:
            print(
                f"Product ID: {row[0]} | "
                f"Product: {row[1]} | "
                f"Available Stock: {row[2]}"
            )

    finally:
        cursor.close()


# ==========================================
# SALES FUNCTIONS
# ==========================================

def record_sale(product_id, quantity_sold):

    cursor = connection.cursor()

    try:
        # Retrieve product information
        cursor.execute(
            "SELECT * FROM products WHERE product_id = %s",
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            print("Product not found.")
            return

        available_stock = product[2]

        # Validate quantity
        if quantity_sold <= 0:
            print("Quantity sold must be positive.")
            return

        if quantity_sold > available_stock:
            print("Insufficient stock.")
            return

        # Calculate total price
        unit_price = product[3]
        total_price = quantity_sold * unit_price

        print("\n========== SALE DETAILS ==========")
        print(f"Product: {product[1]}")
        print(f"Quantity Sold: {quantity_sold}")
        print(f"Unit Price: GH₵{unit_price:,.2f}")
        print(f"Total Price: GH₵{total_price:,.2f}")

        # Deduct stock only if sufficient stock remains
        cursor.execute(
            """
            UPDATE products
            SET quantity = quantity - %s
            WHERE product_id = %s AND quantity >= %s
            """,
            (quantity_sold, product_id, quantity_sold)
        )

        if cursor.rowcount == 0:
            print("Insufficient stock or product not found.")
            connection.rollback()
            return

        # Record the sale
        cursor.execute(
            """
            INSERT INTO sales
            (product_id, quantity_sold, total_price)
            VALUES (%s, %s, %s)
            """,
            (product_id, quantity_sold, total_price)
        )

        # Commit both operations
        connection.commit()

        print("\nSale recorded successfully!")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        connection.rollback()

    finally:
        cursor.close()


def display_sales_history():
    cursor = connection.cursor()

    try:
        query = """
            SELECT *
            FROM sales
            ORDER BY sale_date DESC
        """

        cursor.execute(query)
        sales_history = cursor.fetchall()

        if not sales_history:
            print("No sales recorded yet.")
            return

        print("\n========== SALES HISTORY ==========")

        for sale in sales_history:
            print(f"Sale ID: {sale[0]}")
            print(f"Product ID: {sale[1]}")
            print(f"Quantity Sold: {sale[2]}")
            print(f"Total Price: GH₵{sale[3]:,.2f}")
            print(f"Sale Date: {sale[4]}")
            print("-" * 40)

    finally:
        cursor.close()


# ==========================================
# REVENUE AND TRANSACTION FUNCTIONS
# ==========================================

def calculate_total_revenue():
    cursor = connection.cursor()

    try:
        query = "SELECT COALESCE(SUM(total_price), 0) FROM sales"
        cursor.execute(query)

        total_revenue = cursor.fetchone()[0]

        return total_revenue

    finally:
        cursor.close()


def calculate_total_transactions():
    cursor = connection.cursor()

    try:
        query = "SELECT COUNT(*) FROM sales"
        cursor.execute(query)

        total_count = cursor.fetchone()[0]

        return total_count

    finally:
        cursor.close()


def today_revenue_report():
    cursor = connection.cursor()

    try:
        query = """
            SELECT COALESCE(SUM(total_price), 0)
            FROM sales
            WHERE DATE(sale_date) = CURDATE()
        """

        cursor.execute(query)
        todays_revenue = cursor.fetchone()[0]

        print(f"Today's Revenue: GH₵{todays_revenue:,.2f}")

    finally:
        cursor.close()


def monthly_revenue_report():
    cursor = connection.cursor()

    try:
        query = """
            SELECT COALESCE(SUM(total_price), 0)
            FROM sales
            WHERE MONTH(sale_date) = MONTH(CURDATE())
            AND YEAR(sale_date) = YEAR(CURDATE())
        """

        cursor.execute(query)
        monthly_revenue = cursor.fetchone()[0]

        print(f"This Month's Revenue: GH₵{monthly_revenue:,.2f}")

    finally:
        cursor.close()


def today_transaction_count():
    cursor = connection.cursor()

    try:
        query = """
            SELECT COUNT(*)
            FROM sales
            WHERE DATE(sale_date) = CURDATE()
        """

        cursor.execute(query)
        todays_count = cursor.fetchone()[0]

        print(f"Today's Transaction Count: {todays_count}")

    finally:
        cursor.close()


# ==========================================
# PRODUCT REVENUE REPORTS
# ==========================================

def product_revenue_report():
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                product_id,
                SUM(total_price) AS product_revenue
            FROM sales
            GROUP BY product_id
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No product revenue data available.")
            return

        print("\n========== PRODUCT REVENUE BY ID ==========")

        for row in results:
            print(
                f"Product ID: {row[0]} | "
                f"Revenue: GH₵{row[1]:,.2f}"
            )

    finally:
        cursor.close()


def revenue_report_join():
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                products.product_name,
                SUM(sales.total_price) AS product_revenue
            FROM products
            INNER JOIN sales
                ON products.product_id = sales.product_id
            GROUP BY products.product_id, products.product_name
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No product revenue data available.")
            return

        print("\n========== PRODUCT REVENUE BY NAME ==========")

        for row in results:
            print(
                f"Product: {row[0]} | "
                f"Revenue: GH₵{row[1]:,.2f}"
            )

    finally:
        cursor.close()


def all_products_revenue_report():
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                products.product_name,
                COALESCE(SUM(sales.total_price), 0) AS product_revenue
            FROM products
            LEFT JOIN sales
                ON products.product_id = sales.product_id
            GROUP BY products.product_id, products.product_name
            ORDER BY product_revenue DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print("\n========== ALL PRODUCTS REVENUE ==========")

        for row in results:
            print(
                f"Product: {row[0]} | "
                f"Revenue: GH₵{row[1]:,.2f}"
            )

    finally:
        cursor.close()


def high_revenue_products():
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                products.product_name,
                SUM(sales.total_price) AS total_revenue
            FROM products
            INNER JOIN sales
                ON products.product_id = sales.product_id
            GROUP BY products.product_id, products.product_name
            HAVING SUM(sales.total_price) > 2000
            ORDER BY total_revenue DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No products have generated revenue above GH₵2,000.")
            return

        print("\n========== HIGH REVENUE PRODUCTS ==========")

        for row in results:
            print(
                f"Product: {row[0]} | "
                f"Revenue: GH₵{row[1]:,.2f}"
            )

    finally:
        cursor.close()


# ==========================================
# SALES PERFORMANCE REPORTS
# ==========================================

def daily_sales_report():
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                DATE(sale_date) AS sales_day,
                SUM(total_price) AS daily_revenue
            FROM sales
            GROUP BY DATE(sale_date)
            ORDER BY sales_day ASC
        """

        cursor.execute(query)
        daily_sales = cursor.fetchall()

        if not daily_sales:
            print("No daily sales data available.")
            return

        print("\n========== DAILY SALES REPORT ==========")

        for row in daily_sales:
            print(
                f"Date: {row[0]} | "
                f"Revenue: GH₵{row[1]:,.2f}"
            )

    finally:
        cursor.close()


def best_selling_products():
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                products.product_name,
                SUM(sales.quantity_sold) AS total_quantity_sold
            FROM products
            INNER JOIN sales
                ON products.product_id = sales.product_id
            GROUP BY products.product_id, products.product_name
            ORDER BY total_quantity_sold DESC
        """

        cursor.execute(query)
        best_selling = cursor.fetchall()

        if not best_selling:
            print("No sales data available.")
            return

        print("\n========== BEST SELLING PRODUCTS ==========")

        for row in best_selling:
            print(
                f"Product: {row[0]} | "
                f"Quantity Sold: {row[1]:,}"
            )

    finally:
        cursor.close()


# ==========================================
# REPORTS MENU
# ==========================================

def reports_menu():

    while True:

        print("\n========== REPORTS MENU ==========")
        print("1. Total Revenue")
        print("2. Total Transactions")
        print("3. Today's Revenue")
        print("4. Monthly Revenue")
        print("5. Today's Transaction Count")
        print("6. Product Revenue by ID")
        print("7. Product Revenue by Name")
        print("8. All Products Revenue")
        print("9. High Revenue Products")
        print("10. Daily Sales Report")
        print("11. Best Selling Products")
        print("12. Low Stock Report")
        print("13. Back to Main Menu")

        choice = input("\nEnter your choice: ")

        try:

            if choice == "1":
                revenue = calculate_total_revenue()
                print(f"\nTotal Revenue: GH₵{revenue:,.2f}")

            elif choice == "2":
                transactions = calculate_total_transactions()
                print(f"\nTotal Transactions: {transactions:,}")

            elif choice == "3":
                today_revenue_report()

            elif choice == "4":
                monthly_revenue_report()

            elif choice == "5":
                today_transaction_count()

            elif choice == "6":
                product_revenue_report()

            elif choice == "7":
                revenue_report_join()

            elif choice == "8":
                all_products_revenue_report()

            elif choice == "9":
                high_revenue_products()

            elif choice == "10":
                daily_sales_report()

            elif choice == "11":
                best_selling_products()

            elif choice == "12":
                threshold = int(input("Enter stock threshold: "))
                low_stock_report(threshold)

            elif choice == "13":
                break

            else:
                print("Invalid choice. Please try again.")

        except ValueError:
            print("Please enter a valid number.")

        except mysql.connector.Error as e:
            print(f"Database error: {e}")


# ==========================================
# MAIN MENU
# ==========================================

try:

    while True:

        print("\n========== SHOP MANAGEMENT SYSTEM ==========")
        print("1. Display Products")
        print("2. Record a Sale")
        print("3. Display Sales History")
        print("4. Reports Menu")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        try:

            if choice == "1":
                display_products()

            elif choice == "2":

                product_id = int(input("Enter Product ID: "))
                quantity_sold = int(input("Enter Quantity Sold: "))

                if product_id <= 0:
                    print("Product ID must be positive.")

                else:
                    record_sale(product_id, quantity_sold)

            elif choice == "3":
                display_sales_history()

            elif choice == "4":
                reports_menu()

            elif choice == "5":
                print("Exiting Shop Management System.")
                break

            else:
                print("Invalid choice. Please try again.")

        except ValueError:
            print("Please enter valid numbers.")

        except mysql.connector.Error as e:
            print(f"Database error: {e}")

finally:

    if connection.is_connected():
        connection.close()
        print("Database connection closed.")