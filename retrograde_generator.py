import json
import datetime
from flatlib.geopos import GeoPos
from astro_utils import create_chart
from flatlib import const

def generate_retrogrades_file():
    # קואורדינטות פתח תקווה
    location = GeoPos("32n5", "34e53")

    # תאריך ושעה נוכחיים
    now = datetime.datetime.now()
    date_str = now.strftime("%Y/%m/%d")
    time_str = now.strftime("%H:%M")

    # מפת טרנזיט
    chart = create_chart(date_str, time_str, location)

    # כוכבים שרלוונטיים לנסיגה
    planets = [const.MERCURY, const.VENUS, const.MARS,
               const.JUPITER, const.SATURN,
               const.URANUS, const.NEPTUNE, const.PLUTO]

    retro_data = {}

    for planet_name in planets:
        try:
            planet = chart.get(planet_name)
            retro_data[planet.id] = {"retrograde": planet.retro}
        except Exception:
            retro_data[planet_name] = {"retrograde": False}

    # שמירה לקובץ JSON
    with open("retrogrades.json", "w", encoding="utf-8") as f:
        json.dump(retro_data, f, ensure_ascii=False, indent=2)

    print("✅ קובץ retrogrades.json נוצר בהצלחה")

if __name__ == "__main__":
    generate_retrogrades_file()

