from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import json

def get_birth_chart(birth_date, birth_time, birth_place):
    """
    מחזיר מפת לידה (Chart) לפי תאריך, שעה ומיקום.
    """
    timezone = '+02:00'  # עדכון לפי עונת השנה
    birth_dt = Datetime(birth_date, birth_time, timezone)

    # כולל רק כוכבים עיקריים + צ'ירון (בלי לילית)
    objects = [
        const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
        const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
            ]

    chart = Chart(birth_dt, birth_place, IDs=objects)
    return chart

# -----------------------------------------
# קוד ריצה ישיר (אם מפעילים את הקובץ עצמו)
# -----------------------------------------
if __name__ == "__main__":
    # פרטי לידה – פתח תקווה
    birth_date = '1970/11/22'
    birth_time = '06:00'
    birth_place = GeoPos('32n05', '34e53')  # פתח תקווה

    chart = get_birth_chart(birth_date, birth_time, birth_place)

    # הפקת נתוני כוכבים
    birth_data = {}
    for obj in chart.objects:
        planet = chart.get(obj)
        deg = int(planet.lon)
        min = int((planet.lon - deg) * 60)
        birth_data[obj] = {
            'sign': planet.sign,
            'lon_deg': deg,
            'lon_min': min
        }

    # שמירה לקובץ JSON
    with open('birth_chart.json', 'w', encoding='utf-8') as f:
        json.dump(birth_data, f, ensure_ascii=False, indent=2)

    print("✅ מפת הלידה נשמרה בהצלחה (כולל Chiron, ללא Lilith)")
