import os
import json
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.datetime import Datetime

def dms_format(degrees):
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int((((degrees - d) * 60) - m) * 60)
    return f"{d}°{m:02d}′{s:02d}″"

def load_birth_chart():
    if os.path.exists("birth_chart.json"):
        with open("birth_chart.json", "r", encoding="utf-8") as f:
            return json.load(f)

    # נתוני לידה
    birth_date = "1970/11/22"
    birth_time = "06:00"
    location = GeoPos("32n5", "34e53")
    datetime = Datetime(birth_date, birth_time, '+02:00')  # פתח תקווה בישראל

    # כוכבים לבחירה כולל Chiron ו־Lilith
    planets = [
        'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
        'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
        'Chiron', 'Lilith',
        'ASC', 'MC', 'Node'
    ]

    chart = Chart(datetime, location, IDs=planets)

    chart_data = {}
    for obj in chart.objects:
        chart_data[obj.id] = {
            "sign": obj.sign,
            "lon": round(obj.lon, 6),
            "lat": round(obj.lat, 6),
            "house": obj.house,
            "speed": obj.speed,
            "retrograde": obj.retro,
            "dms": dms_format(obj.lon)
        }

    with open("birth_chart.json", "w", encoding="utf-8") as f:
        json.dump(chart_data, f, ensure_ascii=False, indent=2)

    print("✅ קובץ birth_chart.json נוצר כולל כל הכוכבים (כולל Chiron, Lilith, ASC, MC)")
    return chart_data
