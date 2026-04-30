import sqlite3
import pandas as pd

def get_query_data(query):
    """General helper for SQL queries."""
    conn = sqlite3.connect('kirana_store.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_business_metrics():
    """Calculates live totals for Revenue and Udhaar."""
    sales = get_query_data("SELECT SUM(amount) as total FROM sales WHERE date(timestamp) = date('now')")
    udhaar = get_query_data("SELECT SUM(amount) as total FROM khata")
    
    return {
        "revenue": sales['total'][0] if pd.notna(sales['total'][0]) else 0,
        "udhaar": udhaar['total'][0] if pd.notna(udhaar['total'][0]) else 0
    }

def fetch_logs():
    """Fetches formatted data for charts and tables."""
    debtors = get_query_data("SELECT customer, SUM(amount) as 'Total Owed' FROM khata GROUP BY customer")
    recent_sales = get_query_data("SELECT item, amount, timestamp FROM sales ORDER BY id DESC LIMIT 10")
    inventory = get_query_data("SELECT item_name, quantity, price FROM inventory")
    
    return debtors, recent_sales, inventory