import json
import os

SESSION_FILE = "sessions.json"
user_sessions = {}

def load_sessions():
    """🔥 THE FIX: Loads memory from disk so the bot survives server restarts."""
    global user_sessions
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                user_sessions = json.load(f)
        except Exception as e:
            print(f"Memory Load Error: {e}")
            user_sessions = {}

def save_sessions():
    """Saves current memory state to the hard drive."""
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(user_sessions, f)
    except Exception as e:
        print(f"Memory Save Error: {e}")

# Initialize memory immediately when the server boots
load_sessions()

def get_context(chat_id):
    """Retrieves the last 3 messages for this specific chat."""
    # JSON keys are strictly strings, so we enforce string types
    return user_sessions.get(str(chat_id), [])

def update_context(chat_id, user_msg, bot_msg):
    """Saves interaction, prunes old ones, truncates text, and writes to disk."""
    chat_str = str(chat_id)
    
    if chat_str not in user_sessions:
        user_sessions[chat_str] = []
    
    # 🔥 THE FIX: Protect the AI from massive copy-paste text walls
    safe_user_msg = str(user_msg)[:500] + "..." if len(str(user_msg)) > 500 else str(user_msg)
    safe_bot_msg = str(bot_msg)[:500] + "..." if len(str(bot_msg)) > 500 else str(bot_msg)
    
    user_sessions[chat_str].append({"user": safe_user_msg, "bot": safe_bot_msg})
    
    # Keep only the last 3 turns so we don't overload the AI
    user_sessions[chat_str] = user_sessions[chat_str][-3:]
    
    # Save to disk instantly
    save_sessions()