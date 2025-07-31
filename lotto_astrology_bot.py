from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const, aspects
from datetime import datetime as dt
import pytz

# הגדרות
BIRTH_DATE = '1970-11-22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')  # פתח תקווה
TIMEZONE = 'Asia/Jerusalem'

# רק הכוכבים הנתמכים ע"י flatlib
PLANETS = [
    const.SUN, const.MOON, const.MERCURY,
    const.VENUS, const.MARS, const.JUPITER, const.SATURN
]

MAJOR_ASPECTS = ['CONJ', 'OPP', 'SQR', 'TRI', 'SEX']

def create_chart(date, time):
    return Chart(Datetime(date, time, '+02:00'), BIRTH_PLACE)

def analyze_hour(current_date, hour):
    score = 0
    reasons = []

    try:
        time_str = f'{hour:02d}:00'
        birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
        transit_chart = create_chart(current_date, time_str)

        for obj in PLANETS:
            try:
                natal = birth_chart.get(obj)
                transit = transit_chart.get(obj)

                if not hasattr(natal, 'lon') or not hasattr(transit, 'lon'):
                    reasons.append(f"שגיאה בניתוח {obj}: אובייקט שגוי (אין לו מיקום אסטרולוגי)")
                    continue

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

    except Exception as e:
        score = -999
        reasons.append(f"שגיאה ביצירת מפות אסטרולוגיות: {e}")

    return {
        'hour': f'{hour:02d}:00',
        'score': score,
        'reasons': reasons
    }

def daily_forecast():
    tz = pytz.timezone(TIMEZONE)
    today = dt.now(tz).strftime('%Y-%m-%d')
    results = []

    for hour in [5, 8, 11, 14, 17, 20]:
        result = analyze_hour(today, hour)
        results.append(result)

    best = max(results, key=lambda r: r['score'])

    print("🔮 תחזית אסטרולוגית יומית למילוי לוטו:\n")
    for res in results:
        print(f"🕒 {res['hour']} – ניקוד: {res['score']}")
        for r in res['reasons']:
            print(f"- {r}")
        print()

    print(f"🎯 שעת המזל הטובה ביותר היום: {best['hour']} (ניקוד: {best['score']})")

if __name__ == '__main__':
    daily_forecast()
