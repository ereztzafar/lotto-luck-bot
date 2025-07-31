from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, aspects
import os
import requests
from datetime import datetime, timedelta
from pytz import timezone

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')

# קביעת אזור זמן לפי תאריך (שעון חורף/קיץ)
def get_timezone():
    today = datetime.utcnow()
    year = today.year
    summer_start = datetime(year, 3, 29)
    winter_start = datetime(year, 10, 27)
    return '+03:00' if summer_start <= today < winter_start else '+02:00'

# טעינת משתני סביבה (GitHub Secrets)
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID ב־Secrets")
    return token, chat_id

# שליחת הודעה בטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code}")

# קבלת תחזית אסטרולוגית לשעה מסוימת
def get_forecast_for_hour(hour):
    base_date = datetime.utcnow().strftime('%Y/%m/%d')
    tz = get_timezone()
    dt = Datetime(base_date, f"{hour:02d}:00", tz)

    try:
        birth_dt = Datetime(BIRTH_DATE, BIRTH_TIME, tz)
        birth_chart = Chart(birth_dt, BIRTH_PLACE)
        transit_chart = Chart(dt, BIRTH_PLACE)
    except Exception as e:
        return f"❌ שגיאה ביצירת מפות אסטרולוגיות: {e}"

    forecast = f"🕒 שעה {hour:02d}:00 – תחזית:
"
    score = 0
    reasons = []

    for obj in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
                const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]:

        natal = birth_chart.get(obj)
        transit = transit_chart.get(obj)
        angle = aspects.getAspect(natal.lon, transit.lon)

        if hasattr(transit, 'retro') and transit.retro and obj in [const.MERCURY, const.VENUS, const.MARS]:
            score -= 1
            reasons.append(f"{obj} בנסיגה – השפעה מאטה (-1)")

        if angle in aspects.MAJOR_ASPECTS:
            if angle == aspects.CONJUNCTION:
                score += 2
                reasons.append(f"{obj} בצמידות ללידה – אנרגיה חזקה (+2)")
            elif angle in [aspects.TRINE, aspects.SEXTILE]:
                score += 1
                reasons.append(f"{obj} בזווית הרמונית ללידה – זרימה חיובית (+1)")
            elif angle in [aspects.SQUARE, aspects.OPPOSITION]:
                score -= 1
                reasons.append(f"{obj} בזווית מאתגרת – שיבושים אפשריים (-1)")

    return (hour, score, reasons)

# חישוב כל התחזיות לשעות היום
def daily_luck_forecast():
    best_hour = None
    best_score = -999
    messages = []

    for hour in range(5, 23, 3):
        hour_val, score, reasons = get_forecast_for_hour(hour)
        messages.append(f"\n🕒 {hour_val:02d}:00 – ניקוד: {score}\n" + '\n'.join(f"- {r}" for r in reasons))
        if score > best_score:
            best_score = score
            best_hour = hour_val

    summary = f"🎯 השעה הטובה ביותר היום למילוי לוטו היא {best_hour:02d}:00 (ניקוד {best_score})\n"
    full_forecast = summary + '\n'.join(messages)
    return full_forecast.strip()

# הרצה ישירה
if __name__ == "__main__":
    message = daily_luck_forecast()
    send_telegram_message(message)
