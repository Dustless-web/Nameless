import httpx
import sqlite3
from config import OPENWEATHER_API_KEY, NEWS_API_KEY

async def get_market_vitals():
    """Scrapes top business/commodity news relevant to retail."""
    url = f"https://newsapi.org/v2/everything?q=commodity+prices+India+retail&apiKey={NEWS_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            articles = res.json().get("articles", [])[:3]
            return [a['title'] for a in articles]
    except: return []

async def get_climate_vitals():
    """Fetches weather for the store's area."""
    # Location is determined by the store's registration
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Bengaluru&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            data = res.json()
            return {
                "temp": data['main']['temp'],
                "condition": data['weather'][0]['main']
            }
    except: return None

async def generate_business_advice(db_payload):
    """The brain that connects all dots."""
    news = await get_market_vitals()
    weather = await get_climate_vitals()
    
    # Construct the 'Consultant' Prompt
    prompt = f"""
    You are Basanti, a retail strategy consultant for a Kirana store.
    
    DATA INPUTS:
    - Weather: {weather['condition'] if weather else 'Clear'}, {weather['temp'] if weather else '25'}°C
    - Market News: {news}
    - Inventory: {db_payload['inventory'][:5]}
    - Popular Items: {db_payload['popular_items']}
    
    TASK: Give 2 short, witty, and highly actionable business tips. 
    Format: Use 'Environment Tip' and 'Market Tip'. 
    Example: "Rain is coming! Put the umbrellas near the door and prep the chai-biscuit combos."
    """
    
    # Call your LLM (Gemini/Groq) here to get the advice string
    # For now, we return a mock response for the demo:
    return "Heavy rain is forecast for tomorrow. Move the biscuits to the front counter and check umbrella stock. Also, news indicates a potential hike in dairy prices—consider updating your milk margins."