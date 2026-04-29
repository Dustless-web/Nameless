import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Securely load the Groq Key
# Make sure you add GROQ_API_KEY to your .env file!
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_kirana_data(image_url=None, text=None):
    prompt = """
    You are a Kirana Advisor. Extract items into JSON.
    Format: {"items": [{"name": str, "qty": int, "total": float}], "advice": str}
    Advice must be in Hinglish.
    """

    try:
        # Groq is incredibly fast. We'll use Llama 3.3 70B.
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"User Update: {text}",
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"} # Groq forces JSON perfectly
        )

        # Groq returns a clean dictionary directly
        return json.loads(chat_completion.choices[0].message.content)

    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return {"items": [], "advice": "Mafi chahta hoon, Groq network down hai. Fir try karein?"}