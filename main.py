import httpx
import os
import asyncio
import sqlite3
from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.templating import Jinja2Templates
from config import TELEGRAM_TOKEN, TELEGRAM_API_URL
from database import init_db, get_dashboard_payload, log_chat, nuke_database
from memory import get_context, update_context, user_sessions
from inventory import process_inventory_file
from ai_core import analyze_kirana_data

init_db()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

async def proactive_stock_alert():
    """Runs in the background and sends an alert if stock drops dangerously low."""
    print("⏳ Basanti Alert System Armed...")
    while True:
        # Check every 30 seconds for the demo
        await asyncio.sleep(30) 
        
        try:
            conn = sqlite3.connect('kirana_store.db')
            c = conn.cursor()
            c.execute("SELECT item_name, quantity FROM inventory WHERE quantity < 10 AND quantity > 0")
            low_stock = c.fetchall()
            conn.close()

            if low_stock and user_sessions:
                alert_text = "🚨 *BASANTI AUTO-ALERT* 🚨\n\nBoss, we are running critically low on:\n"
                for item in low_stock:
                    alert_text += f"• {item[0]} (Only {item[1]} left!)\n"
                
                alert_text += "\nText me to restock when the supplier arrives!"

                admin_chat_id = list(user_sessions.keys())[0]
                
                send_telegram_message(admin_chat_id, alert_text)
                log_chat("Basanti Auto-Alert", alert_text)

                print("🚨 Alert fired! Sleeping for 5 minutes to prevent spam.")
                await asyncio.sleep(300) 
                
        except Exception as e:
            print(f"Alert System Error: {e}")

@app.on_event("startup")
async def startup_event():
    """Starts the heartbeat loop the exact second Uvicorn boots up."""
    asyncio.create_task(proactive_stock_alert())

@app.get("/test")
def test_route():
    return {"status": "Basanti is alive and the code updated!"}

# --- UI ROUTES ---
@app.get("/")
@app.get("/dashboard")
async def dashboard(request: Request):
    data = get_dashboard_payload()
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "data": data})

@app.get("/api/sales/all")
async def get_all_sales():
    """Hidden endpoint to fetch the entire sales history for the PDF exporter."""
    conn = sqlite3.connect('kirana_store.db')
    try:
        import pandas as pd
        all_sales = pd.read_sql_query("SELECT timestamp, item, amount FROM sales ORDER BY id DESC", conn).to_dict(orient="records")
        return {"status": "success", "data": all_sales}
    except Exception as e:
        print(f"Export Error: {e}")
        return {"status": "error", "data": []}
    finally:
        conn.close()

@app.post("/api/nuke")
async def api_nuke_database():
    """Endpoint to trigger the total data wipe."""
    nuke_database()
    log_chat("SYSTEM", "☢️ ALL DATA TERMINATED BY ADMIN ☢️")
    return {"status": "success", "message": "Database wiped clean."}

# --- BOT LOGIC ---
def send_telegram_message(chat_id, text_message):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text_message, "parse_mode": "Markdown"}
    try:
        httpx.post(url, json=payload, timeout=15.0).raise_for_status()
    except Exception as e:
        print(f"❌ Telegram send error: {e}")

def get_telegram_file_url(file_id):
    try:
        response = httpx.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}", timeout=10.0)
        file_info = response.json()
        if file_info.get("ok"):
            return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info['result']['file_path']}"
    except Exception as e:
        print(f"File URL fetch error: {e}")
    return None

def format_bot_response(analysis):
    intent = analysis.get("type", "chat")
    advice = analysis.get("advice", "Error processing request.")
    
    if intent == "sale":
        return f"✅ *Sale Logged*\nAmount: ₹{analysis.get('amount', 0)}\n\n💡 {advice}"
    elif intent == "expense":
        return f"📉 *Deduction*\nAmount: ₹{analysis.get('amount', 0)}\n\n💡 {advice}"
    elif intent == "restock":
        return f"📦 *Inventory Restocked*\n\n{advice}"
    elif intent == "report":
        return f"📊 *Report*\n{advice}" 
    return f"🤖 {advice}"

def process_telegram_update(message: dict):
    try:
        chat_id = message["chat"]["id"]

        if "text" in message:
            text = message["text"]
            log_chat("User", text) 
            
            # 🔥 THE ORACLE INTERCEPTOR 🔥
            if text.strip().lower() == "/advice":
                # 1. Grab current state of the business
                payload = get_dashboard_payload()
                
                # 2. Pass it to the advisor engine
                from advisor import generate_business_advice
                
                # process_telegram_update runs in a sync thread pool, so we use asyncio.run to await the API calls safely
                advice = asyncio.run(generate_business_advice(payload))
                
                # 3. Log and send the strategic brief
                log_chat("Basanti Oracle", advice)
                send_telegram_message(chat_id, f"💡 *BASANTI STRATEGY BRIEF*\n\n{advice}")
                return # Exit early! We don't want the standard AI trying to log this as a sale.
            
            analysis = analyze_kirana_data(text=text, history=get_context(chat_id))
            reply = format_bot_response(analysis)
            
            log_chat("Basanti", reply) 
            send_telegram_message(chat_id, reply)
            update_context(chat_id, text, reply)
            
        elif "voice" in message:
            url = get_telegram_file_url(message["voice"]["file_id"])
            if url:
                log_chat("User", "🎤 [Sent a Voice Note]")
                analysis = analyze_kirana_data(audio_url=url, history=get_context(chat_id))
                reply = format_bot_response(analysis)
                
                log_chat("Basanti", reply)
                send_telegram_message(chat_id, reply)
                
        elif "photo" in message:
            url = get_telegram_file_url(message["photo"][-1]["file_id"])
            if url:
                log_chat("User", "📸 [Uploaded a Receipt]")
                analysis = analyze_kirana_data(image_url=url)
                reply = format_bot_response(analysis)
                
                log_chat("Basanti", reply)
                send_telegram_message(chat_id, reply)
                
        elif "document" in message:
            doc = message["document"]
            if doc.get("file_name", "").lower().endswith(('.csv', '.xlsx')):
                url = get_telegram_file_url(doc["file_id"])
                if url:
                    log_chat("User", f"📄 [Uploaded File: {doc['file_name']}]")
                    result = process_inventory_file(url, doc["file_name"])
                    
                    log_chat("Basanti", result)
                    send_telegram_message(chat_id, result)
                    
    except Exception as e:
        print(f"Background Processing Error: {e}")
        try:
            send_telegram_message(message["chat"]["id"], "⚠️ I ran into an error processing that request.")
        except:
            pass

# --- WEBHOOK ENDPOINT ---
@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        if "message" in body:
            background_tasks.add_task(process_telegram_update, body["message"])
            
        return Response(content="OK", status_code=200)
        
    except Exception as e:
        print(f"Webhook Reception Error: {e}")
        return Response(content="OK", status_code=200)