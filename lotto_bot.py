import os
import requests
from datetime import datetime

def send_telegram_message(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

def get_astrology_message():
    now = datetime.now()
    hour = now.hour
    time_str = now.strftime("%H:%M")

    # שעות מזל לדוגמה – נעדכן בשלב הבא לפי תחזית אסטרולוגית אמיתית
    lucky_hours = {
        6: "הכוכבים מאירים – התחלה טובה למלא לוטו!",
        9: "שיקול דעת נדרש – לא למהר!",
        12: "זמן ביניים – שים לב לאינטואיציה.",
        15: "שעה נוחה להימורים קטנים.",
        18: "יש פוטנציאל להפתעות חיוביות.",
        21: "המזל לצדך – אם לא היום, אז מחר.",
    }

    if hour in lucky_hours:
        return f"🕒 {time_str} – {lucky_hours[hour]}"
    else:
        return f"🕒 {time_str} – לא שעה אסטרולוגית מוגדרת."

if __name__ == "__main__":
    message = get_astrology_message()
    send_telegram_message(message)

