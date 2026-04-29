import sqlite3
from datetime import datetime

DB_NAME = "kirana_store.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create a table to store every item sold
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity REAL,
            total_price REAL,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def log_sale(items):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for item in items:
        cursor.execute(
            "INSERT INTO sales (item_name, quantity, total_price, timestamp) VALUES (?, ?, ?, ?)",
            (item.get('name'), item.get('qty'), item.get('total'), timestamp)
        )
    
    conn.commit()
    conn.close()
    print(f"✅ Successfully logged {len(items)} items to the DB.")

# Initialize the DB once when this file is first loaded
init_db()