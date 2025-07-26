import json
import requests
from datetime import datetime

def load_secrets():
    with open("secrets.json", "r") as file:
        data = json.load(file)
        return data["BOT_TOKEN"], data["CHAT_ID"]

def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

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
    return f"🕒 {time_str} – {lucky_hours.get(hour, 'לא שעה אסטרולוגית מוגדרת.')}"

if __name__ == "__main__":
    message = get_astrology_message()
    send_telegram_message(message)


