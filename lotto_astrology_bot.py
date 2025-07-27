from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import os
import requests
from datetime import datetime

# נתוני לידה — תאריך, שעה, מיקום (פתח תקווה)
BIRTH_DATE = '1970-11-22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos(32.0833, 34.8833)  # ערכים מספריים, לא מחרוזת

# טוקן וצ'אט ID מה-secrets
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ אין TELEGRAM_TOKEN או TELEGRAM_CHAT_ID בסודות GitHub")
    return token, chat_id

# שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

# תחזית אסטרולוגית לפי מפת הטרנזיט הנוכחית
def get_astrology_forecast():
    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    transit_dt = Datetime(dt, 'UTC')
    chart = Chart(transit_dt, BIRTH_PLACE)

    sun = chart.get('SUN')
    moon = chart.get('MOON')
    jupiter = chart.get('JUPITER')

    forecast = f"""
🔮 תחזית אסטרולוגית לשעה {transit_dt.time}:

☀️ שמש במזל {sun.sign}
🌙 ירח במזל {moon.sign}
♃ צדק במזל {jupiter.sign}

🧠 הערכה כללית: לא שעת מזל אסטרולוגית מוגדרת.
"""
    return forecast.strip()

# הרצת התחזית ושליחה לטלגרם
if __name__ == "__main__":
    message = get_astrology_forecast()
    send_telegram_message(message)
