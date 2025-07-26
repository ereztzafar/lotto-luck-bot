from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import os
import requests
from datetime import datetime

# ⚙️ פרטי הלידה שלך - פתח תקווה, 22/11/1970, 06:00
BIRTH_DATE = '1970-11-22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos(32.0833, 34.8833)  # פתח תקווה

# 🔑 טעינת הטוקן והצ'אט מטוקני GitHub Secrets
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסרים TELEGRAM_TOKEN או TELEGRAM_CHAT_ID בסודות GitHub")
    return token, chat_id

# 📤 שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📬 Status: {response.status_code} | {message}")

# 🔮 תחזית אסטרולוגית לפי הטרנזיט הנוכחי
def get_astrology_forecast():
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    transit_dt = Datetime(now, 'UTC')
    chart = Chart(transit_dt, BIRTH_PLACE)

    # דוגמה: בדיקת השמש והירח
    sun = chart.get(const.SUN)
    moon = chart.get(const.MOON)

    forecast = (
        f"🪐 תחזית אסטרולוגית לשעה {now}:\n"
        f"☀️ שמש ב-{sun.sign} ({sun.lon:.2f}°)\n"
        f"🌙 ירח ב-{moon.sign} ({moon.lon:.2f}°)\n"
        f"💡 יום טוב לפעולה עם אנרגיה של {sun.sign} ולביטוי רגשי לפי {moon.sign}."
    )
    return forecast

# 🚀 הפעלה ראשית
if __name__ == '__main__':
    message = get_astrology_forecast()
    send_telegram_message(message)
