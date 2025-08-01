import os
import json
from flatlib.geopos import GeoPos
from astro_utils import create_chart

def format_dms(decimal_degrees):
    degrees = int(decimal_degrees)
    minutes_full = (decimal_degrees - degrees) * 60
    minutes = int(minutes_full)
    seconds = int((minutes_full - minutes) * 60)
    return f"{degrees}°{minutes:02d}′{seconds:02d}″"

def load_birth_chart():
    if os.path.exists("birth_chart.json"):
        with open("birth_chart.json", "r", encoding="utf-8") as f:
            chart_data = json.load(f)
        return chart_data

    # פרטי הלידה שלך
    birth_date = "1970/11/22"
    birth_time = "06:00"
    location = GeoPos("32n5", "34e53")

    chart = create_chart(birth_date, birth_time, location)
    chart_data = {}

    for obj in chart.objects:
        chart_data[obj.id] = {
            "sign": obj.sign,
            "lon": obj.lon,
            "lon_dms": format_dms(obj.lon),
            "lat": obj.lat,
            "house": obj.house,
            "speed": obj.speed,
            "retrograde": obj.retro
        }

    # הוספת נקודות מיוחדות – האופק (ASC) וה-MC
    chart_data["ASC"] = {
        "sign": chart.Asc.sign,
        "lon": chart.Asc.lon,
        "lon_dms": format_dms(chart.Asc.lon)
    }

    chart_data["MC"] = {
        "sign": chart.MC.sign,
        "lon": chart.MC.lon,
        "lon_dms": format_dms(chart.MC.lon)
    }

    with open("birth_chart.json", "w", encoding="utf-8") as f:
        json.dump(chart_data, f, ensure_ascii=False, indent=2)

    print("✅ קובץ birth_chart.json נוצר בהצלחה.")
    return chart_data
