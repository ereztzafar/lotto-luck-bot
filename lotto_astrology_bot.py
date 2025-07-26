import os
import requests
from datetime import datetime
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const

# 🎯 פרטי לידה אישיים
BIRTH_DATE = '1970-11-22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos(32.0833, 34.8833)   # פתח תקווה

# 📦 טוען סודות מ־GitHub Actions
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID בסודות של GitHub")
    return token, chat_id

# 📤 שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

# 🔮 תחזית אסטרולוגית חכמה
def get_astrology_forecast():
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    birth = Datetime(BIRTH_DATE, BIRTH_TIME, '+02:00')
    transit = Datetime(now, '+00:00')  # זמן נוכחי ב־UTC

    # תרשים לידה ותרשים טרנזיט
    natal_chart = Chart(birth, BIRTH_PLACE)
    transit_chart = Chart(transit, BIRTH_PLACE)

    moon = transit_chart.get(const.MOON)
    jupiter = transit_chart.get(const.JUPITER)
    sun = transit_chart.get(const.SUN)

    forecast = f"""🔮 תחזית אסטרולוגית אישית לשעה {transit.date.split()[1]}:

☀️ השמש במזל {sun.sign}
🌙 הירח במזל {moon.sign}
♃ יופיטר במזל {jupiter.sign}
"""

    # ניתוח לפי השפעות
    if moon.sign == 'Virgo' and jupiter.sign in ['Taurus', 'Cancer']:
        forecast += "\n💡 זהו זמן עם פוטנציאל טוב במיוחד! כדאי לשקול הגרלות או לוטו."
    elif moon.sign == 'Scorpio':
        forecast += "\n⚠️ מצב רגשי מורכב – כדאי להיות זהיר בהחלטות כספיות."
    elif jupiter.sign == 'Leo':
        forecast += "\n🎉 יופיטר מעודד ביטחון עצמי – פעל בביטחון!"
    else:
        forecast += "\n🕰 אין כרגע שילוב חזק – אולי בהמשך היום."

    return forecast

if __name__ == "__main__":
    msg = get_astrology_forecast()
    send_telegram_message(msg)

