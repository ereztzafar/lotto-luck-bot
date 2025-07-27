from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import requests
import os
from datetime import datetime

# פרטי לידה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n5', '34e53')  # פתח תקווה

# קביעת אזור זמן לפי שעון קיץ/חורף בישראל
def get_timezone():
    today = datetime.utcnow()
    year = today.year
    summer_start = datetime(year, 3, 28)  # שעון קיץ: מ-28/03
    winter_start = datetime(year, 10, 30)  # שעון חורף: מ-30/10

    if summer_start <= today < winter_start:
        return '+03:00'  # שעון קיץ
    else:
        return '+02:00'  # שעון חורף

# טעינת טוקן וצ'אט ID מתוך סודות GitHub
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID ב-secrets")
    return token, chat_id

# שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | נשלח בהצלחה")

# יצירת תחזית אסטרולוגית
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

☀️ השמש במזל: {sun.sign} ({sun.lon}°)
🌙 הירח במזל: {moon.sign} ({moon.lon}°)
♃ יופיטר במזל: {jupiter.sign} ({jupiter.lon}°)
"""
    if moon.sign == 'Virgo' and jupiter.sign in ['Taurus', 'Cancer']:
        forecast += "\n💡 זמן מזל גבוה! כדאי למלא לוטו או חישגד."
    elif moon.sign == 'Scorpio':
        forecast += "\n⚠️ זהירות: עלולים להיות מתחים רגשיים."
    elif jupiter.sign == 'Leo':
        forecast += "\n🎉 הזדמנות נדירה לפעולה חיובית."
    else:
        forecast += "\n🕰 אין השפעה אסטרולוגית מיוחדת כרגע."

    return forecast.strip()

# הרצה ושליחה
if __name__ == "__main__":
    message = get_astrology_forecast()
    send_telegram_message(message)
