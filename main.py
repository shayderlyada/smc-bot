from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = "8648698110:AAF2KPxg92LE9JYrTCbZcLmFaDl2w_MDahs"
CHAT_ID = "-1003891592823"

TG_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.body()
    text = data.decode("utf-8", errors="ignore")

    print("RAW SIGNAL:", text)

    requests.post(TG_URL, json={
        "chat_id": CHAT_ID,
        "text": f"🚨 SMC SIGNAL:\n{text}"
    })

    return {"ok": True}
