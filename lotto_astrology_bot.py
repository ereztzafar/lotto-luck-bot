from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import requests
import os
from datetime import datetime

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_TZ = '+02:00'  # שעון חורף (ישראל)
BIRTH_PLACE = GeoPos('32n05', '34e53')  # פתח תקווה

# קביעת אזור זמן לפי תאריך (שעון חורף/קיץ בישראל)
def get_timezone():
    now = datetime.utcnow()
    year = now.year
    # ישראל עוברת לשעון קיץ ביום שישי האחרון של מרץ
    # וחוזרת לשעון חורף ביום ראשון האחרון של אוקטובר
    dst_start = max(
        datetime(year, 3, d) for d in range(25, 32)
        if datetime(year, 3, d).weekday() == 4  # שישי
    )
    dst_end = max(
        datetime(year, 10, d) for d in range(25, 32)
        if datetime(year, 10, d).weekday() == 6  # ראשון
    )
    return '+03:00' if dst_start <= now < dst_end else '+02:00'

# טעינת סודות מה־GitHub Secrets
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID ב־Secrets")
    return token, chat_id

# שליחת הודעה
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code}")

# חישוב תחזית אסטרולוגית
def get_astrology_forecast():
    tz = get_timezone()
    now = datetime.utcnow().strftime('%Y/%m/%d %H:%M')
    dt = Datetime(now.split()[0], now.split()[1], tz)
    chart = Chart(dt, BIRTH_PLACE)

    sun = chart.get(const.SUN)
    moon = chart.get(const.MOON)
    jupiter = chart.get(const.JUPITER)

    forecast = f"""
🔮 תחזית אסטרולוגית לשעה {dt.time} (UTC{tz}):

☀️ השמש במזל: {sun.sign} ({float(sun.lon):.2f}°)
🌙 הירח במזל: {moon.sign} ({float(moon.lon):.2f}°)
♃ יופיטר במזל: {jupiter.sign} ({float(jupiter.lon):.2f}°)
""".strip()

    if moon.sign == 'Virgo' and jupiter.sign in ['Taurus', 'Cancer']:
        forecast += "\n\n💡 זמן מזל גבוה! כדאי למלא לוטו או חישגד."
    elif moon.sign == 'Scorpio':
        forecast += "\n\n⚠️ זהירות: עלולים להיות מתחים רגשיים."
    elif jupiter.sign == 'Leo':
        forecast += "\n\n🎉 הזדמנות נדירה לפעולה חיובית."
    else:
        forecast += "\n\n🕰 אין השפעה אסטרולוגית מיוחדת כרגע."

    return forecast

# הפעלה
if __name__ == "__main__":
    message = get_astrology_forecast()
    send_telegram_message(message)
