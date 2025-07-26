import os
import requests

def send_telegram_message(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Sent Telegram message: {response.status_code}")

# דוגמה לשימוש
if __name__ == "__main__":
    send_telegram_message("✅ הבוט של הלוטו הופעל בהצלחה!")
