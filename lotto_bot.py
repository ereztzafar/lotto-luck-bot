import os
import requests
from datetime import datetime

def send_telegram_message(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ חסרים ערכים ל־TELEGRAM_TOKEN או TELEGRAM_CHAT_ID במשתני סביבה.")
        exit(1)

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
