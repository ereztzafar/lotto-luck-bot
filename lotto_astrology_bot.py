from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import requests
import os
from datetime import datetime

# נתוני לידה של ארז
BIRTH_DATE = '1970-11-22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32.0833', '34.8833')  # פתח תקווה

# שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# בניית מפת לידה
def get_natal_chart():
    dt = Datetime(BIRTH_DATE, BIRTH_TIME, '+02:00')
    return Chart(dt, BIRTH_PLACE)

# בניית מפת טרנזיט לזמן נוכחי
def get_transit_chart():
    now = datetime.now()
    dt = Datetime(now.strftime('%Y-%m-%d'), now.strftime('%H:%M'), '+02:00')
    return Chart(dt, BIRTH_PLACE)

# ניתוח בסיסי של כוכבים בטרנזיט
def analyze_transits(natal, transit):
    results = []
    for planet in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER]:
        nat = natal.get(planet)
        trans = transit.get(planet)
        angle = abs(nat.lon - trans.lon)
        if angle < 8 or abs(angle - 360) < 8:
            results.append(f"🔮 {planet} ב־קונבנציה (צמוד) – עוצמה גבוהה")
        elif abs(angle - 180) < 8:
            results.append(f"⚠️ {planet} באופוזיציה – אתגר זמני")
    return results

# הרצת הבוט
if __name__ == "__main__":
    natal = get_natal_chart()
    transit = get_transit_chart()
    analysis = analyze_transits(natal, transit)

    now = datetime.now().strftime("%H:%M %d/%m")
    header = f"🪐 תחזית אסטרולוגית {now}"
    message = '\n'.join([header] + analysis if analysis else [header, "היום אין השפעות משמעותיות."])

    send_telegram_message(message)
