from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import json
import datetime

def get_current_retrogrades():
    now = datetime.datetime.now()
    date = now.strftime('%Y/%m/%d')
    time = now.strftime('%H:%M')
    pos = GeoPos("32n5", "34e53")  # מיקום פתח תקווה

    chart = Chart(date, time, pos)
    retrogrades = []
    for planet in [const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN,
                   const.URANUS, const.NEPTUNE, const.PLUTO]:
        obj = chart.get(planet)
        if obj.retro:
            retrogrades.append(obj.id)

    return retrogrades

def save_to_file(retrogrades):
    with open("retrogrades.json", "w", encoding='utf-8') as f:
        json.dump({
            "date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            "retrogrades": retrogrades
        }, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    retrogrades = get_current_retrogrades()
    save_to_file(retrogrades)
    print(f"✅ נשמרו {len(retrogrades)} כוכבים בנסיגה לקובץ retrogrades.json")
