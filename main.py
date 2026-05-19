import os
import time
import requests

TOKEN = os.getenv("8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs")
CHAT_ID = os.getenv("-1003891592823")

def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("NO TOKEN OR CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def main():
    print("BOT STARTING...")

    send_message("✅ Бот запущен и работает")

    while True:
        try:
            print("alive tick")
            time.sleep(30)

        except Exception as e:
            print("loop error:", e)
            send_message(f"ERROR: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
