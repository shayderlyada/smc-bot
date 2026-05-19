import os
import time
import requests
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# =========================
# TELEGRAM CONFIG
# =========================

TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"

# =========================
# FAKE WEB SERVER (Render FIX)
# =========================

def run_server():
    port = int(os.environ.get("PORT", 10000))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"SMC bot alive")

    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

# =========================
# TELEGRAM SENDER
# =========================

def send_telegram(message: str):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print("Telegram error:", e)

# =========================
# PRICE FETCH (BINANCE)
# =========================

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

# =========================
# SIMPLE SMC LOGIC (CLEAN VERSION)
# =========================

prices = []

def check_signal(prices):
    if len(prices) < 20:
        return None

    recent = prices[-20:]
    last = recent[-1]

    high = max(recent)
    low = min(recent)

    if last > high * 0.999:
        return ("LONG", last, low)

    if last < low * 1.001:
        return ("SHORT", last, high)

    return None

# =========================
# MAIN LOOP
# =========================

print("SMC BOT STARTED")

while True:
    try:
        price = get_price()
        prices.append(price)

        print("price:", price)

        signal = check_signal(prices)

        if signal:
            side, entry, level = signal

            msg = f"""
🚨 SMC SIGNAL

Side: {side}
Entry: {entry}

SL Level: {level}
"""

            send_telegram(msg)
            print("SIGNAL SENT")

            prices = prices[-100:]

    except Exception as e:
        print("ERROR:", e)

    time.sleep(3)
