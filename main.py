from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from processor import analyze_kirana_data
from database import log_sale  # <--- New Import

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(None), MediaUrl0: str = Form(None)):
    # 1. AI Analysis
    advice_dict = analyze_kirana_data(text=Body)
    
    # 2. Database Logging
    # We extract the 'items' list from the AI's JSON and save it
    items_to_log = advice_dict.get("items", [])
    if items_to_log:
        log_sale(items_to_log)
    
    # 3. Response Formatting
    advice_text = advice_dict.get("advice", "Mafi chahta hoon, network error.")
    twiml_response = MessagingResponse()
    twiml_response.message(advice_text)
    
    return Response(content=str(twiml_response), media_type="application/xml")