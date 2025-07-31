from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, aspects
import os
import requests
from datetime import datetime

# זוויות אסטרולוגיות עיקריות
MAJOR_ASPECTS = ['CONJ', 'OPP', 'SQR', 'TRI', 'SEX']

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')

# קביעת אזור זמן לפי שעון ישראל (קיץ/חורף)
def get_timezone():
    today = datetime.utcnow()
    year = today.year
    summer_start = datetime(year, 3, 29)
    winter_start = datetime(year, 10, 27)
    return '+03:00' if summer_start <= today < winter_start else '+02:00'

# טעינת משתני סביבה (טלגרם)
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID ב־Secrets")
    return token, chat_id

# שליחת הודעה בטלגרם
def send_telegram_message(message: str):
    if not message or not message.strip():
        print("⚠️ לא נשלחה הודעה — הטקסט ריק.")
        return

    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ שגיאה בשליחה לטלגרם: {response.text}")
    else:
        print("✅ ההודעה נשלחה בהצלחה.")

# חיזוי לשעה מסוימת
def get_forecast_for_hour(hour):
    base_date = datetime.utcnow().strftime('%Y/%m/%d')
    tz = get_timezone()
    dt = Datetime(base_date, f"{hour:02d}:00", tz)

    try:
        birth_dt = Datetime(BIRTH_DATE, BIRTH_TIME, tz)
        birth_chart = Chart(birth_dt, BIRTH_PLACE)
        transit_chart = Chart(dt, BIRTH_PLACE)
    except Exception as e:
        return (hour, -999, [f"שגיאה ביצירת מפות אסטרולוגיות: {e}"])

    score = 0
    reasons = []

    for obj in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
                const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]:

        try:
            natal = birth_chart.get(obj)
            transit = transit_chart.get(obj)
            angle = aspects.getAspect(natal.lon, transit.lon, MAJOR_ASPECTS)

            if hasattr(transit, 'retro') and transit.retro and obj in [const.MERCURY, const.VENUS, const.MARS]:
                score -= 1
                reasons.append(f"{obj} בנסיגה – השפעה מאטה (-1)")

            if angle:
                if angle == 'CONJ':
                    score += 2
                    reasons.append(f"{obj} בצמידות ללידה – אנרגיה חזקה (+2)")
                elif angle in ['TRI', 'SEX']:
                    score += 1
                    reasons.append(f"{obj} בזווית הרמונית – זרימה חיובית (+1)")
                elif angle in ['SQR', 'OPP']:
                    score -= 1
                    reasons.append(f"{obj} בזווית מאתגרת – שיבושים אפשריים (-1)")

        except Exception as inner_e:
            reasons.append(f"שגיאה בניתוח {obj}: {inner_e}")

    return (hour, score, reasons)

# תחזית לכל היום
def daily_luck_forecast():
    best_hour = None
    best_score = -999
    messages = []

    for hour in range(5, 23, 3):  # שעות: 05:00, 08:00, ..., 20:00
        hour_val, score, reasons = get_forecast_for_hour(hour)
        messages.append(f"\n🕒 {hour_val:02d}:00 – ניקוד: {score}\n" + '\n'.join(f"- {r}" for r in reasons))
        if score > best_score:
            best_score = score
            best_hour = hour_val

    if best_hour is not None and best_score > -999:
        summary = f"\n🎯 שעת המזל הטובה ביותר היום: {best_hour:02d}:00 (ניקוד: {best_score})"
    else:
        summary = "\n⚠️ לא נמצאה שעת מזל מתאימה היום."

    return "🔮 תחזית אסטרולוגית יומית למילוי לוטו:\n" + '\n'.join(messages) + summary

# הרצה ישירה
if __name__ == "__main__":
    message = daily_luck_forecast()
    send_telegram_message(message)
