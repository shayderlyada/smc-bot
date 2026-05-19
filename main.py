import asyncio
import websockets
import json
import requests
import numpy as np
from collections import deque
import time
import sqlite3

# =========================
# CONFIG
# =========================

SYMBOL = "btcusdt"
WS_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@trade"

TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"

TG_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# =========================
# DATABASE (WINRATE LOG)
# =========================

conn = sqlite3.connect("trades.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS trades (
    time TEXT,
    side TEXT,
    entry REAL,
    result TEXT
)
""")
conn.commit()

# =========================
# MARKET DATA
# =========================

prices = deque(maxlen=300)

# =========================
# TELEGRAM
# =========================

def send(msg):
    requests.post(TG_URL, json={
        "chat_id": CHAT_ID,
        "text": msg
    })

# =========================
# SMC CORE FUNCTIONS
# =========================

def get_structure(data):
    highs = max(data)
    lows = min(data)

    return highs, lows


def detect_swing(prices):
    if len(prices) < 50:
        return None

    arr = np.array(prices)

    highs = np.max(arr[-50:])
    lows = np.min(arr[-50:])

    last = arr[-1]

    return highs, lows, last


def liquidity_sweep(prices):
    if len(prices) < 30:
        return False

    recent_high = max(prices[-30:])
    recent_low = min(prices[-30:])
    last = prices[-1]

    # sweep above high then reject
    if last > recent_high:
        return "buy_sweep"

    if last < recent_low:
        return "sell_sweep"

    return None


def bos_choco(prices):
    if len(prices) < 100:
        return None

    highs = max(prices[-100:])
    lows = min(prices[-100:])
    last = prices[-1]

    if last > highs * 0.999:
        return "BOS_UP"

    if last < lows * 1.001:
        return "BOS_DOWN"

    return None


def trend_filter(prices):
    if len(prices) < 50:
        return None

    ema = np.mean(list(prices)[-50:])
    last = prices[-1]

    return "bull" if last > ema else "bear"


def fvg_filter(prices):
    if len(prices) < 3:
        return False

    # simplified imbalance detection
    if abs(prices[-1] - prices[-2]) > np.std(prices[-20:]):
        return True

    return False


# =========================
# SIGNAL ENGINE
# =========================

last_signal_time = 0


def generate_signal(prices):
    global last_signal_time

    if time.time() - last_signal_time < 60:  # anti spam 1 min
        return None

    sweep = liquidity_sweep(prices)
    bos = bos_choco(prices)
    trend = trend_filter(prices)
    fvg = fvg_filter(prices)

    last = prices[-1]

    # LONG setup
    if sweep == "buy_sweep" and trend == "bull" and fvg:
        entry = last
        sl = min(prices[-20:])
        tp = entry + (entry - sl) * 2

        last_signal_time = time.time()

        return ("LONG", entry, sl, tp)

    # SHORT setup
    if sweep == "sell_sweep" and trend == "bear" and fvg:
        entry = last
        sl = max(prices[-20:])
        tp = entry - (sl - entry) * 2

        last_signal_time = time.time()

        return ("SHORT", entry, sl, tp)

    return None


# =========================
# TELEGRAM FORMAT
# =========================

def send_signal(side, entry, sl, tp):
    msg = f"""
🚨 PRO SMC ENGINE

📊 Side: {side}

🎯 Entry: {round(entry, 2)}
🛑 SL: {round(sl, 2)}
🎯 TP: {round(tp, 2)}

⚙️ RR: 1:2
"""

    send(msg)


# =========================
# WINRATE LOG
# =========================

def log_trade(side, entry):
    c.execute("INSERT INTO trades VALUES (?, ?, ?, ?)",
              (time.ctime(), side, entry, "OPEN"))
    conn.commit()


# =========================
# BINANCE STREAM
# =========================

async def run():
    async with websockets.connect(WS_URL) as ws:
        while True:
            try:
                data = await ws.recv()
                data = json.loads(data)

                price = float(data['p'])
                prices.append(price)

                signal = generate_signal(prices)

                if signal:
                    side, entry, sl, tp = signal

                    send_signal(side, entry, sl, tp)
                    log_trade(side, entry)

            except Exception as e:
                print("error:", e)
                await asyncio.sleep(1)


# =========================
# START
# =========================

asyncio.run(run())
