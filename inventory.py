import io
import sqlite3
import httpx
import pandas as pd

def process_inventory_file(file_url, file_name):
    """Downloads, scrubs, and securely upserts an inventory file into the database."""
    print(f"📥 Processing inventory file: {file_name}")
    try:
        # Added a strict timeout to prevent the worker thread from hanging
        response = httpx.get(file_url, timeout=15.0)
        response.raise_for_status()
        file_data = response.content
        
        # Parse the file based on extension
        if file_name.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_data))
        elif file_name.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_data))
        else:
            return "❌ Unsupported file type. Please send a CSV or Excel (.xlsx) file."

        # Sanitize column names
        df.columns = [str(col).strip().lower() for col in df.columns]
        required = {'item', 'quantity', 'price'}
        
        if not required.issubset(set(df.columns)):
            return f"❌ Missing columns! File needs: Item, Quantity, Price. Found: {list(df.columns)}"

        # Rename for database consistency
        df.rename(columns={'item': 'item_name'}, inplace=True)

        # 🔥 THE FIX: Data Sanitation Pipeline
        # Force numeric types and drop garbage/empty rows
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df.dropna(subset=['item_name', 'quantity', 'price'], inplace=True)

        # Open DB connection
        conn = sqlite3.connect('kirana_store.db')
        c = conn.cursor()
        
        items_updated = 0
        items_added = 0

        # 🔥 THE FIX: Smart Upsert Logic (Prevents Duplicates)
        for _, row in df.iterrows():
            name = str(row['item_name']).strip()
            qty = int(row['quantity'])
            price = float(row['price'])
            
            # Check if item already exists
            c.execute("SELECT quantity FROM inventory WHERE item_name = ?", (name,))
            existing = c.fetchone()
            
            if existing:
                # Add to existing stock and update to latest price
                c.execute("UPDATE inventory SET quantity = quantity + ?, price = ? WHERE item_name = ?", (qty, price, name))
                items_updated += 1
            else:
                # Insert brand new item
                c.execute("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                items_added += 1

        conn.commit()
        conn.close()
        
        return f"✅ **Inventory Synced!**\n📦 New Items Added: {items_added}\n🔄 Existing Stock Updated: {items_updated}"

    except httpx.ReadTimeout:
        return "❌ Telegram took too long to send the file. Please try again."
    except Exception as e:
        print(f"File processing error: {e}")
        return "❌ Failed to read the file. Ensure it follows the exact format (Item, Quantity, Price)."