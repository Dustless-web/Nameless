import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('kirana_store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY, item TEXT, amount REAL, timestamp DATE DEFAULT CURRENT_DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory 
                 (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_logs 
                 (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp DATETIME DEFAULT (datetime('now', 'localtime')))''')
    conn.commit()
    conn.close()

def log_chat(sender, message):
    conn = sqlite3.connect('kirana_store.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO chat_logs (sender, message) VALUES (?, ?)", (sender, str(message)))
        conn.commit()
    except Exception as e:
        print(f"Chat Log Error: {e}")
    finally:
        conn.close()

def get_db_context():
    """Compiles live inventory and sales velocity for the AI to analyze."""
    conn = sqlite3.connect('kirana_store.db')
    c = conn.cursor()
    try:
        # 1. Today's Revenue
        c.execute("SELECT SUM(amount) FROM sales WHERE date(timestamp) = date('now', 'localtime')")
        today_sales = c.fetchone()[0] or 0
        
        # 2. Current Inventory Snapshot
        c.execute("SELECT item_name, quantity, price FROM inventory LIMIT 100")
        inv = c.fetchall()
        inv_dict = {r[0]: r[1] for r in inv}
        
        # 3. Calculate Sales Velocity (What is actually moving?)
        c.execute("SELECT item FROM sales")
        sales_rows = c.fetchall()
        sold_counts = {}
        for row in sales_rows:
            # Parse the "2x Milk, 1x Bread" formatting
            parts = [p.strip() for p in str(row[0]).split(',')]
            for p in parts:
                name = p.split('x ')[-1] if 'x ' in p else p
                sold_counts[name] = sold_counts.get(name, 0) + 1
                
        # 4. Identify Dead Stock (Items sitting in inventory with ZERO sales)
        dead_stock = [item for item in inv_dict.keys() if item not in sold_counts]
        
        # 5. Identify Top Sellers
        top_sellers = sorted(sold_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_sellers_str = ", ".join([f"{k} ({v} sold)" for k, v in top_sellers])

        # 6. Format the string for the AI
        inv_list = ", ".join([f"{r[0]} (Qty: {r[1]}, ₹{r[2]})" for r in inv])
        
        context = f"[LIVE STATS] Today: ₹{today_sales}\n"
        context += f"[INVENTORY] {inv_list}\n"
        context += f"[TOP SELLERS] {top_sellers_str if top_sellers_str else 'No sales yet'}\n"
        context += f"[DEAD STOCK (0 Sales)] {', '.join(dead_stock) if dead_stock else 'None'}"
        
        return context
    except Exception as e:
        print(f"DB Context Error: {e}")
        return "[STATS] Error loading database."
    finally:
        conn.close()

def get_dashboard_payload():
    conn = sqlite3.connect('kirana_store.db')
    try:
        # Basic Stats
        sales_today = pd.read_sql_query("SELECT SUM(amount) as total FROM sales WHERE date(timestamp) = date('now', 'localtime')", conn)['total'][0] or 0
        inventory = pd.read_sql_query("SELECT item_name, quantity, price FROM inventory", conn).to_dict(orient="records")
        recent_sales = pd.read_sql_query("SELECT item, amount, timestamp FROM sales ORDER BY id DESC LIMIT 10", conn).to_dict(orient="records")
        chat_logs = pd.read_sql_query("SELECT sender, message, timestamp FROM chat_logs ORDER BY id DESC LIMIT 50", conn).to_dict(orient="records")

        # 🔥 Daily Revenue Comparison (Forced Zero Filling for Chart.js) 🔥
        raw_revenue = pd.read_sql_query("""
            SELECT date(timestamp) as date, SUM(amount) as total 
            FROM sales 
            WHERE timestamp >= date('now', '-7 days')
            GROUP BY date(timestamp)
        """, conn).to_dict(orient="records")
        
        # Convert DB results into a quick dictionary
        revenue_dict = {row['date']: row['total'] for row in raw_revenue}
        
        # Build a perfect 7-day array, filling missing days with 0
        daily_revenue = []
        today = datetime.now()
        for i in range(6, -1, -1):
            target_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_revenue.append({
                "date": target_date[-5:], # Keep it clean like "04-30"
                "total": revenue_dict.get(target_date, 0)
            })

        # Popular Items Analysis
        all_sales_text = pd.read_sql_query("SELECT item FROM sales", conn)
        item_counts = {}
        for row in all_sales_text['item']:
            parts = [p.strip() for p in str(row).split(',')]
            for p in parts:
                name = p.split('x ')[-1] if 'x ' in p else p
                item_counts[name] = item_counts.get(name, 0) + 1
        
        popular_items = sorted([{"name": k, "count": v} for k, v in item_counts.items()], key=lambda x: x['count'], reverse=True)[:5]

        # BUSINESS HEALTH REPORT METRICS 
        c = conn.cursor()
        c.execute("SELECT COUNT(id), AVG(amount) FROM sales WHERE date(timestamp) = date('now', 'localtime')")
        sales_stats = c.fetchone()
        orders_today = sales_stats[0] if sales_stats[0] else 0
        aov = round(sales_stats[1], 2) if sales_stats[1] else 0
        
        c.execute("SELECT COUNT(id) FROM inventory WHERE quantity < 10 AND quantity > 0")
        low_stock_count = c.fetchone()[0] or 0
        
        health_status = "CRITICAL" if low_stock_count > 3 else ("IDLE" if orders_today == 0 else "OPTIMAL")
        
        health_report = {
            "orders_today": orders_today,
            "aov": aov,
            "low_stock_count": low_stock_count,
            "status": health_status
        }

        return {
            "revenue": round(sales_today, 2), 
            "sales": recent_sales, 
            "inventory": inventory,
            "chat_logs": chat_logs,
            "daily_revenue": daily_revenue,
            "popular_items": popular_items,
            "health": health_report
        }
    finally:
        conn.close()

def execute_db_action(analysis):
    intent = analysis.get("type")
    if intent not in ["sale", "expense", "restock"]: return analysis 
    conn = sqlite3.connect('kirana_store.db')
    c = conn.cursor()
    try:
        if intent == "sale":
            items = analysis.get("items", [])
            final_total, logged_items = 0, []
            for item in items:
                name, qty = item.get("name", "").strip(), item.get("qty", 1)
                c.execute("SELECT price, quantity FROM inventory WHERE item_name LIKE ?", (f"%{name}%",))
                row = c.fetchone()
                if row:
                    price = row[0] * qty
                    c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_name LIKE ?", (qty, f"%{name}%"))
                    final_total += price
                    logged_items.append(f"{qty}x {name}")
            if logged_items:
                c.execute("INSERT INTO sales (item, amount) VALUES (?, ?)", (", ".join(logged_items), final_total))
                conn.commit()
                analysis.update({"amount": final_total, "advice": f"Logged {', '.join(logged_items)} for ₹{final_total}."})
        elif intent == "restock":
            for item in analysis.get("items", []):
                name, qty = item.get("name", "").strip(), item.get("qty", 1)
                c.execute("SELECT id FROM inventory WHERE item_name LIKE ?", (f"%{name}%",))
                row = c.fetchone()
                if row: c.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
                else: c.execute("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, 0)", (name, qty))
            conn.commit()
    finally:
        conn.close()
    return analysis

def nuke_database():
    conn = sqlite3.connect('kirana_store.db')
    c = conn.cursor()
    try:
        c.execute("DELETE FROM sales")
        c.execute("DELETE FROM inventory")
        c.execute("DELETE FROM chat_logs")
        try:
            c.execute("DELETE FROM sqlite_sequence WHERE name IN ('sales', 'inventory', 'chat_logs')")
        except sqlite3.OperationalError:
            pass 
        conn.commit()
    except Exception as e:
        print(f"Database Nuke Error: {e}")
    finally:
        conn.close()
