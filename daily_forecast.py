from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import aspects
from flatlib import const
from lotto_bot import send_telegram_message
from datetime import datetime

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
TIMEZONE = '+02:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')

OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
    const.CHIRON
]

def start_forecast():
    now = datetime.now()
    header = f"📆 תחזית ליום {now.strftime('%d/%m/%Y')}:\n"
    header += "🔭 מפת לידה והיבטים בין כוכבים:\n"

    birth_dt = Datetime(BIRTH_DATE, BIRTH_TIME, TIMEZONE)
    chart = Chart(birth_dt, BIRTH_PLACE, IDs=OBJECTS)

    aspect_checker = AspectChecker(chart, aspects=MAJOR_ASPECTS)
    found_aspects = aspect_checker.allAspects()

    aspect_lines = []
    for aspect in found_aspects:
        obj1 = aspect.obj1
        obj2 = aspect.obj2
        aspect_type = aspect.type
        angle = round(aspect.orb)  # Or use aspect.angle if needed

        line = f"🔹 {obj1} ({chart.get(obj1).sign}) ⬄ {obj2} ({chart.get(obj2).sign}) - היבט: {aspect_type} ({angle}°)"
        aspect_lines.append(line)

    message = header + "\n".join(aspect_lines)
    print(message)
    send_telegram_message(message)

if __name__ == "__main__":
    start_forecast()
