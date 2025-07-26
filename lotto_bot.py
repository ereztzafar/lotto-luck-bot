import json
import requests
from datetime import datetime

def load_secrets():
    try:
        with open("secrets.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data["BOT_TOKEN"], data["CHAT_ID"]
    except Exception as e:
        print(f"❌ שגיאה בקריאת secrets.json: {e}")
        exit(1)

def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    if response.ok:
        print(f"📤 נשלחה הודעה לטלגרם ({response.status_code})")
    else:
        print(f"❌ שגיאה בשליחה ({response.status_code}): {response.text}")

def get_astrology_message():
    now = datetime.now()
    hour = now.hour
    time_str = now.strftime("%H:%M")

    lucky_hours = {
        6: "הכוכבים מאירים – התחלה טובה למלא לוטו!",
        9: "שיקול דעת נדרש – לא למהר!",
        12: "זמן ביניים – שים לב לאינטואיציה.",
        15: "שעה נוחה להימורים קטנים.",
        18: "יש פוטנציאל להפתעות חיוביות.",
        21: "המזל לצדך – אם לא היום, אז מחר.",
    }

    message = lucky_hours.get(hour, "❌ לא שעה אסטרולוגית מוגדרת.")
    return f"🕒 {time_str} – {message}"

if __name__ == "__main__":
    message = get_astrology_message()
    send_telegram_message(message)



