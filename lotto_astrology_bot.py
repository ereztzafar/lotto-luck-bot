import requests
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const, aspects
from datetime import datetime as dt
import pytz
import os

# ============ הגדרות אישיות ============

BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')  # פתח תקווה
TIMEZONE = 'Asia/Jerusalem'

PLANETS = [
    const.SUN, const.MOON, const.MERCURY,
    const.VENUS, const.MARS, const.JUPITER, const.SATURN
]

MAJOR_ASPECTS = ['CONJ', 'OPP', 'SQR', 'TRI', 'SEX']

# טוקן ו-Chat ID מתוך משתני סביבה או קבועים ישירות
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7688538382:AAEwE4vlaivb8nqyI9JEGU5FDO4LGTqywMI')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '813610615')


# ============ פונקציות עיקריות ============

def create_chart(date, time):
    return Chart(Datetime(date, time, '+02:00'), BIRTH_PLACE)

def analyze_hour(current_date, hour):
    score = 0
    reasons = []

    try:
        time_str = f'{hour:02d}:00'
        if '-' in current_date:
            current_date = current_date.replace('-', '/')

        birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
        transit_chart = create_chart(current_date, time_str)

        for obj in PLANETS:
            try:
                natal = birth_chart.get(obj)
                transit = transit_chart.get(obj)

                if not hasattr(natal, 'lon') or not hasattr(transit, 'lon'):
                    reasons.append(f"שגיאה בניתוח {obj}: נתון אסטרולוגי שגוי")
                    continue

                angle = aspects.getAspect(natal.lon, transit.lon)

                if isinstance(angle, str) and angle in MAJOR_ASPECTS:
                    if angle == 'CONJ':
                        score += 2
                        reasons.append(f"{obj} בצמידות ללידה – אנרגיה חזקה (+2)")
                    elif angle in ['TRI', 'SEX']:
                        score += 1
                        reasons.append(f"{obj} בזווית הרמונית – זרימה חיובית (+1)")
                    elif angle in ['SQR', 'OPP']:
                        score -= 1
                        reasons.append(f"{obj} בזווית מאתגרת – שיבושים אפשריים (-1)")

                if hasattr(transit, 'retro') and transit.retro and obj in [const.MERCURY, const.VENUS, const.MARS]:
                    score -= 1
                    reasons.append(f"{obj} בנסיגה – השפעה מאטה (-1)")

            except Exception as inner_e:
                reasons.append(f"שגיאה בניתוח {obj}: {inner_e}")

    except Exception as e:
        score = -999
        reasons.append(f"שגיאה ביצירת מפות אסטרולוגיות: {e}")

    return {
        'hour': f'{hour:02d}:00',
        'score': score,
        'reasons': reasons
    }

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

def daily_forecast():
    tz = pytz.timezone(TIMEZONE)
    today = dt.now(tz).strftime('%Y-%m-%d')
    results = []

    for hour in [5, 8, 11, 14, 17, 20]:
        result = analyze_hour(today, hour)
        results.append(result)

    best = max(results, key=lambda r: r['score'])

    # בניית ההודעה
    message = "🔮 <b>תחזית אסטרולוגית יומית למילוי לוטו</b>:\n\n"
    for res in results:
        message += f"🕒 {res['hour']} – ניקוד: <b>{res['score']}</b>\n"
        for r in res['reasons']:
            message += f"• {r}\n"
        message += "\n"

    message += f"🎯 <b>שעת המזל הטובה ביותר היום: {best['hour']} (ניקוד: {best['score']})</b>"

    # הדפסה לקונסול + שליחה לטלגרם
    print(message)
    send_telegram_message(message)


# ============ הפעלה ראשית ============

if __name__ == '__main__':
    daily_forecast()
