from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# ===== TELEGRAM SETTINGS =====

BOT_TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"


# ===== WEBHOOK DATA MODEL =====

class WebhookData(BaseModel):

    symbol: str
    side: str
    price: str

    choch: bool
    bos: bool
    liquidity_sweep: bool
    order_block: bool
    fvg: bool
    trendline_break: bool
    volume_spike: bool

    rr: float

    tp1: str
    tp2: str
    tp3: str

    sl: str


# ===== HOME =====

@app.get("/")
async def home():
    return {"status": "backend working"}


# ===== WEBHOOK =====

@app.post("/webhook")
async def webhook(data: WebhookData):

    score = 0

    # ===== SCORING =====

    if data.choch:
        score += 2

    if data.bos:
        score += 2

    if data.liquidity_sweep:
        score += 2

    if data.order_block:
        score += 1

    if data.fvg:
        score += 1

    if data.trendline_break:
        score += 1

    if data.volume_spike:
        score += 1

    if data.rr >= 1.5:
        score += 2

    # ===== RR FILTER =====

    if data.rr < 1.5:
        return {
            "status": "rejected",
            "reason": "RR too low"
        }

    # ===== SCORE FILTER =====

    if score < 6:
        return {
            "status": "rejected",
            "reason": "low score"
        }

    # ===== 10/10 SYSTEM =====

    final_score = round((score / 11) * 10, 1)

    # ===== TELEGRAM MESSAGE =====

    message = f"""
⚡ SMART MONEY SIGNAL

Coin: {data.symbol}
Side: {data.side}

Entry: {data.price}

TP1: {data.tp1}
TP2: {data.tp2}
TP3: {data.tp3}

SL: {data.sl}

RR: 1:{data.rr}

Confidence: {final_score}/10
"""

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        telegram_url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

    return {
        "status": "signal sent",
        "confidence": final_score
    }