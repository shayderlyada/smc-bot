import time
import requests

# =========================
# CONFIG
# =========================

TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"

prices = []

# =========================
# TELEGRAM
# =========================

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except Exception as e:
        print("telegram error:", e)

# =========================
# GET PRICE (REST)
# =========================

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

# =========================
# SIMPLE SMC LOGIC
# =========================

def detect_signal(prices):
    if len(prices) < 20:
        return None

    recent = prices[-20:]
    last = recent[-1]
    high = max(recent)
    low = min(recent)

    # LONG breakout
    if last > high * 0.999:
        entry = last
        sl = low
        tp = entry + (entry - sl) * 2

        return ("LONG", entry, sl, tp)

    # SHORT breakout
    if last < low * 1.001:
        entry = last
        sl = high
        tp = entry - (sl - entry) * 2

        return ("SHORT", entry, sl, tp)

    return None

# =========================
# MAIN LOOP
# =========================

print("SMC BOT STARTED...")

while True:
    try:
        price = get_price()
        prices.append(price)

        print("price:", price)

        signal = detect_signal(prices)

        if signal:
            side, entry, sl, tp = signal

            msg = f"""
🚨 SMC SIGNAL

Side: {side}

Entry: {entry}
SL: {sl}
TP: {tp}
"""

            send(msg)
            print("SIGNAL SENT")

            prices = prices[-100:]  # чистим память

    except Exception as e:
        print("error:", e)

    time.sleep(3)


    import os

port = int(os.environ.get("PORT", 10000))

from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"bot alive")

server = HTTPServer(("0.0.0.0", port), Handler)

import threading
threading.Thread(target=server.serve_forever).start()
