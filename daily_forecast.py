from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import aspects, const
from lotto_bot import send_telegram_message
from datetime import datetime

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
TIMEZONE = '+02:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')

# שימוש בקבועים מתוך const במקום ephem.MAJOR_OBJECTS
OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
    const.CHIRON  # הוספת כירון
]

def start_forecast():
    now = datetime.now()
    header = f"📆 תחזית ליום {now.strftime('%d/%m/%Y')}:\n"
    header += "🔭 מפת לידה והיבטים בין כוכבים:\n"

    # יצירת מפת לידה
    birth_dt = Datetime(BIRTH_DATE, BIRTH_TIME, TIMEZONE)
    chart = Chart(birth_dt, BIRTH_PLACE, IDs=OBJECTS)

    aspect_lines = []
    for i in range(len(OBJECTS)):
        for j in range(i + 1, len(OBJECTS)):
            obj1 = chart.get(OBJECTS[i])
            obj2 = chart.get(OBJECTS[j])
            angle = aspects.getAngle(obj1, obj2)  # תיקון כאן!
            aspect_type = aspects.aspectType(obj1, obj2, aspects.MAJOR_ASPECTS)
            if aspect_type:
                line = f"🔹 {obj1.id} ({obj1.sign}) ⬄ {obj2.id} ({obj2.sign}) - היבט: {aspect_type} ({round(angle)}°)"
                aspect_lines.append(line)

    message = header + "\n".join(aspect_lines)
    print(message)
    send_telegram_message(message)

if __name__ == "__main__":
    start_forecast()
