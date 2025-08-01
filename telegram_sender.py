import os
import requests
import json

def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID במשתני הסביבה")
    return token, chat_id

def send_telegram_message(message, token=None, chat_id=None):
    if not token or not chat_id:
        token, chat_id = load_secrets()

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ הודעה נשלחה לטלגרם בהצלחה.")
    except Exception as e:
        print(f"❌ שגיאה בשליחת הודעה לטלגרם: {e}")

