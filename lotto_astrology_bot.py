from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import os
import requests
from datetime import datetime

# פרטי הלידה שלך:
BIRTH_DATE = '1970-11-22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos(32.0833, 34.8833)  # פתח תקווה, ישראל

# טוען טוקן ו-Chat ID מהסודות
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID בסודות של GitHub")
    return token, chat_id

# שולח הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

# תחזית אסטרולוגית חכמה לפי מפת טרנזיט
def get_astrology_forecast():
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    transit_dt = Datetime(now, 'UTC')
    chart = Chart(transit_dt, BIRTH_PLACE)

    sun = chart.get('SUN')
    moon = chart.get('MOON')
    jupiter = chart.get('JUP')

    forecast = f"""🔮 תחזית אסטרולוגית אישית לשעה {transit_dt.time}:

☀️ השמש ב-{sun.sign} {sun.signlon}°
🌙 הירח ב-{moon.sign} {moon.signlon}°
♃ יופיטר ב-{jupiter.sign} {jupiter.signlon}°
"""

    # ניתוח פשוט
    if moon.sign == 'VIR' and jupiter.sign in ['TAU', 'CAN']:
        forecast += "\n💡 זהו זמן מצוין למילוי לוטו או חישגד!"
    elif moon.sign == 'SCO':
        forecast += "\n⚠️ מתחים רגשיים מורגשים – לא הזמן להימורים."
    elif jupiter.sign == 'LEO':
        forecast += "\n🎉 יופיטר נותן ביטחון – זמן טוב לפעול."
    else:
        forecast += "\n🕰 לא זוהתה השפעה חזקה – המתן לשעה אחרת."

    return forecast

if __name__ == "__main__":
    msg = get_astrology_forecast()
    send_telegram_message(msg)
