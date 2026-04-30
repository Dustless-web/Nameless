import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

GROQ_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

if not GROQ_KEY or not TELEGRAM_TOKEN:
    raise ValueError("❌ Missing API Keys in .env file!")
OPENWEATHER_API_KEY = "8b1c9e5f0a7c4d2b9e5f6a7c8d9e0f1"
NEWS_API_KEY = "24b751a33dab4f2c8cd3ccc4004a7190"