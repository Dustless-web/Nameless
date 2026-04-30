import io
import json
import base64
import httpx
from groq import Groq
from config import GROQ_KEY
from database import execute_db_action, get_db_context

client = Groq(api_key=GROQ_KEY)

def safe_json_parse(raw_text):
    """Helper to cleanly strip Markdown wrappers from AI JSON responses."""
    raw_text = raw_text.strip()
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
    return json.loads(raw_text)

def analyze_kirana_data(text=None, audio_url=None, image_url=None, history=None):
    
    # 1. AUDIO PROCESSING
    if audio_url:
        try:
            audio_data = httpx.get(audio_url).content
            translation = client.audio.transcriptions.create(
                file=("voice.ogg", io.BytesIO(audio_data)),
                model="whisper-large-v3-turbo",
                response_format="text"
            )
            text = translation
        except Exception as e:
            print(f"Audio Error: {e}")
            return {"type": "error", "advice": "Sorry, audio processing failed."}

    # 2. VISION PROCESSING (Receipt Scanning)
    if image_url:
        try:
            image_data = httpx.get(image_url).content
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            vision_prompt = """
            Look at this receipt. Find the final GRAND TOTAL amount.
            Respond ONLY with a valid JSON object. Do not add any conversational text.
            Example:
            {"type": "sale", "items": [{"name": "Receipt Items", "qty": 1, "total": 150.0}], "amount": 150.0, "customer": null, "advice": "Scanned receipt."}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": vision_prompt}, 
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                temperature=0.1 
            )
            
            analysis = safe_json_parse(completion.choices[0].message.content)
            return execute_db_action(analysis)
            
        except Exception as e:
            print(f"Vision Parsing Error: {e}")
            return {"type": "error", "advice": "Could not extract a valid total from the receipt."}

    # 3. TEXT / INTENT PROCESSING
    if not text:
        return {"type": "error", "advice": "No input detected."}

    history_str = "".join([f"User: {t['user']}\nBot: {t['bot']}\n" for t in history]) if history else ""
    db_context = get_db_context()

    text_prompt = f"""
    You are Basanti, a highly intelligent Kirana Store manager and data analyst.
    
    👇 ABSOLUTE TRUTH: LIVE DATABASE STATS 👇
    {db_context}
    
    👇 PAST CONVERSATION 👇
    {history_str}
    
    Input: "{text}"
    
    CRITICAL RULES:
    1. Intents: 'sale', 'expense', 'report', 'restock', or 'chat'.
    2. THE AMNESIA RULE: NEVER trust Past Conversation for numbers. ALWAYS use the Live Database Stats.
    3. LOGGING SALES (COMMAND): If the user uses action words like "add X to sales", "sold X", or "bill X", you MUST use the 'sale' intent. If they do not name a specific product (e.g., "Add 1000 to sales"), set the item name to "Manual Entry" and include the "total" key for that item like this: [{{"name": "Manual Entry", "qty": 1, "total": 1000}}]
    4. RESTOCKING (COMMAND): If the user says they "bought", "added", or "received" stock for the store, use the 'restock' intent.
    5. BUSINESS ANALYTICS (REPORT): If the user asks what to stop restocking or what is selling poorly, look at [TOP SELLERS] and [DEAD STOCK]. Use the 'report' intent.
    6. SIMPLE STATS (QUESTION): If the user ASKS A QUESTION like "what is my revenue?", "how much are my sales?", or checks stock, find the exact number in [LIVE STATS]. Use the 'chat' intent. ONLY use this if they are asking a read-only question.
    
    ⚠️ STRICT JSON RULE ⚠️
    You MUST return ONLY a valid JSON object. No conversational text outside the JSON. No markdown blocks. 
    Even for simple answers, format it EXACTLY like this:
    {{ 
      "type": "chat", 
      "items": [], 
      "amount": 0, 
      "advice": "Today's total sales are ₹500." 
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": text_prompt}],
            response_format={"type": "json_object"},
            temperature=0.2 # Keeps the AI focused on exact data extraction
        )
        analysis = safe_json_parse(completion.choices[0].message.content)
        return execute_db_action(analysis)
    except Exception as e:
        print(f"🔥 GROQ API CRASHED: {e}")
        return {"type": "error", "advice": "System busy. Please try again in a moment."}