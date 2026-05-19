from fastapi import FastAPI, Request
import requests
import json

app = FastAPI()

# =========================
# TELEGRAM CONFIG
# =========================
TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"

TG_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send(text: str):
    requests.post(TG_URL, json={
        "chat_id": CHAT_ID,
        "text": text
    })


# =========================
# FORMATTER (SMART)
# =========================
def format_signal(raw: str):

    try:
        data = json.loads(raw)

        side = data.get("side", "UNKNOWN")
        entry = data.get("entry", "N/A")
        sl = data.get("sl", "N/A")
        tp1 = data.get("tp1", "N/A")
        tp2 = data.get("tp2", "N/A")
        tp3 = data.get("tp3", "N/A")
        symbol = data.get("symbol", "UNKNOWN")

        return f"""
🚨 SMC SIGNAL

📊 Symbol: {symbol}
📈 Side: {side}

🎯 Entry: {entry}
🛑 SL: {sl}

🎯 TP1: {tp1}
🎯 TP2: {tp2}
🎯 TP3: {tp3}
"""

    except:
        return f"""
🚨 RAW SIGNAL

{raw}
"""


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "running"}


# =========================
# WEBHOOK (ACCEPT EVERYTHING)
# =========================
@app.api_route("/webhook", methods=["POST", "GET"])
async def webhook(request: Request):

    body = await request.body()
    text = body.decode("utf-8", errors="ignore")

    print("========== RAW INCOMING ==========")
    print(text)
    print("===================================")

    message = format_signal(text)
    send(message)

    return {"ok": True}
