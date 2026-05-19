import time
import requests
import ccxt

# ======================
# TELEGRAM CONFIG
# ======================
TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })
    print("TG:", r.status_code, r.text)


# ======================
# BINANCE SETUP
# ======================
exchange = ccxt.binance()


# ======================
# SIMPLE STRATEGY (EMA CROSS)
# ======================
def get_data():
    ohlcv = exchange.fetch_ohlcv("BTC/USDT", timeframe="1m", limit=50)
    closes = [c[4] for c in ohlcv]
    return closes


def ema(data, period):
    k = 2 / (period + 1)
    e = data[0]
    for price in data:
        e = price * k + e * (1 - k)
    return e


def check_signal(closes):
    ema_fast = ema(closes[-10:], 5)
    ema_slow = ema(closes[-10:], 15)

    print("FAST:", ema_fast, "SLOW:", ema_slow)

    if ema_fast > ema_slow:
        return "LONG"
    elif ema_fast < ema_slow:
        return "SHORT"
    return None


# ======================
# MAIN LOOP
# ======================
def main():
    send_telegram("🚀 BOT STARTED")

    last_signal = None

    while True:
        try:
            closes = get_data()
            signal = check_signal(closes)

            print("SIGNAL:", signal)

            if signal and signal != last_signal:
                msg = f"""
🚨 SMC SIGNAL (TEST VERSION)

PAIR: BTCUSDT
SIDE: {signal}

Price: {closes[-1]}
Timeframe: 1m
"""
                send_telegram(msg)
                last_signal = signal

        except Exception as e:
            print("ERROR:", e)
            send_telegram(f"ERROR: {e}")

        time.sleep(30)


if __name__ == "__main__":
    main()
