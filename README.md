<div align="center">

# ⚡ BASANTI ⚡
**The AI Oracle & Zero-UI Terminal for the Modern Kirana Store**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![Python](https://img.shields.io/badge/Python-3.10+-black?style=for-the-badge&logo=python)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/index.html)
[![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

> India runs on Kirana stores. But the people running them don't have time for complex SaaS dashboards. **Basanti is a manager, not an app.** 

</div>

---

## 🛑 The Problem vs. 🟢 The Basanti Solution

**The Input Bottleneck:** Kirana owners are too busy handing goods to customers to type numbers into a POS system. Because data entry is tedious, they don't do it. Without data, they suffer from dead stock, revenue leakage, and zero analytics.

**The Zero-UI Paradigm:** We eliminated the traditional interface. Basanti lives where the owner already communicates: **Telegram & WhatsApp**. Speak or type naturally (*"I sold 3 milks and a bread"*). Basanti’s AI engine parses the intent, logs the sale, and instantly updates a Neo-Brutalist, real-time analytics terminal.

---

## 🏗️ System Architecture & Workflow

Basanti operates on a decoupled, event-driven architecture that separates the conversational input from the data visualization.
```text
  [ 🏪 Store Owner ] 
         │ 
         │ 🗣️ Voice / Text / Image
         ▼
  [ 📱 Telegram Bot API ] 
         │ 
         │ ⚡ Webhook POST Payload
         ▼
┌────────────────────────────────────────────────────────┐
│ 🚀 BASANTI CORE (FastAPI)                              │
│                                                        │
│  1. Webhook Receiver ──► Adds task to Background Queue │
│  2. AI Intent Router ──► Classifies: Sale/Restock/Chat │
│  3. The Oracle 🧠    ──► Fetches external market data  │
└────────┬───────────────────────────────────────────────┘
         │
         │ 🗄️ SQL Mutations (INSERT/UPDATE)
         ▼
  [ 💽 SQLite3 Database ] ◄─────┐
         │                      │ 🔄 Real-time Polling
         │ 📊 Data Extraction   │
         ▼                      │
  [ 🖥️ Neo-Brutalist Web Terminal ]
  (Tailwind + Chart.js + Jinja2)
```

### 🔄 The Data Workflow
1. **The Ear (Ingestion):** A FastAPI webhook listens for Telegram events. It offloads processing to `BackgroundTasks` to ensure zero-latency webhook responses.
2. **The Brain (AI Core):** User text/audio is sent to the LLM. The prompt is dynamically injected with the *Live Database Context* (current stock, dead stock, today's revenue) to prevent LLM hallucinations.
3. **The Oracle (Context):** For strategic queries, `advisor.py` scrapes OpenWeatherMap and NewsAPI to provide external supply chain insights.
4. **The Ledger (DB):** Validated JSON intents from the AI safely mutate the SQLite database.
5. **The Face (UI):** The browser dashboard continuously hydrates with live data, visualizing daily revenue, top sellers, and communication logs.

---

## 🔥 Core Features

* 🎙️ **Zero-UI Data Entry:** Log sales, record expenses, and restock inventory entirely through natural language text or voice notes.
* 🧠 **The Oracle Engine:** Basanti predicts business needs based on external data (e.g., *"Rain is forecast. Move umbrellas to the front"*).
* 🏥 **Business Vitals Overlay:** Calculates Average Order Value (AOV) and identifies "Dead Stock" automatically.
* ⬛ **Neo-Brutalist Terminal:** High-contrast, maximum-legibility dashboard designed specifically for chaotic, fast-paced store environments.
* 🚨 **Proactive Alerts:** A background heartbeat monitors inventory and pings the owner's phone if critical stock drops below 10 units.
* 📄 **Instant PDF Auditing:** One-click generation of professional sales ledgers directly in the browser via `jsPDF`.

---

## 📂 Project Structure
```bash
📦 basanti-terminal
 ┣ 📂 templates
 ┃ ┗ 📜 index.html        # The Neo-Brutalist Dashboard UI
 ┣ 📜 main.py             # FastAPI Server & Telegram Webhook
 ┣ 📜 ai_core.py          # LLM Prompts & Intent Classification
 ┣ 📜 database.py         # SQLite Queries & Payload Generation
 ┣ 📜 advisor.py          # News/Weather scraping & Strategic AI
 ┣ 📜 memory.py           # Chat history & context management
 ┣ 📜 config.py           # Environment Variables & API Keys
 ┗ 📜 README.md
```

---

## 🚀 Local Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/basanti.git](https://github.com/Dustless-web/basanti.git)
cd basanti
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn httpx pandas sqlite3 jinja2 python-multipart
```

### 3. Environment Configuration
Create a file named `config.py` in the root directory:
```python
# config.py
TELEGRAM_TOKEN = "your_telegram_bot_token"
TELEGRAM_API_URL = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){TELEGRAM_TOKEN}"

# Integrations
LLM_API_KEY = "your_llm_api_key_here" 
OPENWEATHER_API_KEY = "your_openweathermap_key"
NEWS_API_KEY = "your_newsapi_key"
```

### 4. Expose Webhook (Development)
Run ngrok to expose your local server to Telegram:
```bash
ngrok http 8000
```
*Register the generated HTTPS URL with your Telegram Bot via the `setWebhook` API.*

### 5. Boot the System
```bash
uvicorn main:app --reload
```
Navigate to `http://localhost:8000` to view the terminal.

---

## 🎯 Demo Script (Test Cases)

To see Basanti in action, send these exact phrases to your Telegram Bot:

| Action | Phrase to send to Telegram | Expected Result |
| :--- | :--- | :--- |
| **Initialize** | `"Basanti, the supplier arrived. Add 50 Maggi and 100 Eggs."` | Inventory table populates. |
| **Log Sale** | `"Sold 2 Maggi."` | Revenue spikes; Maggi stock drops by 2. |
| **Manual Override**| `"Add 500 rupees to sales."` | Adds a "Manual Entry" to the ledger. |
| **Strategic Advice** | `/advice` | Oracle generates a brief based on weather/news. |
| **Analytics** | `"What item should I stop restocking?"` | AI reads the DB and lists 0-sale items. |

---

## 🔮 Future Roadmap
- [ ] **WhatsApp Business API Integration** (Native Indian market support).
- [ ] **Automated Supplier Ordering:** Trigger SMS to distributors when stock is low.
- [ ] **Voice Cloning:** Basanti responds with conversational voice audio.
- [ ] **Barcode Scanning:** Upload an image of a barcode via Telegram to log items.

---
<div align="center">
  <i>Built with intense focus and excessive caffeine for CODE CARNAGE 2.0.</i>
</div>
```
