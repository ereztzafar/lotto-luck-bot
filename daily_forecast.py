from flatlib import const, aspects
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime

# מיקום הלידה שלך (פתח תקווה)
BIRTH_LOCATION = GeoPos("32n5", "34e53")

def find_lucky_hours(birth_chart, current_chart):
    lucky_hours = []
    now = datetime.datetime.now()

    for hour in range(5, 24, 2):  # כל שעתיים בין 05:00 ל־22:00
        forecast_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        date_str = forecast_time.strftime('%Y/%m/%d')
        time_str = forecast_time.strftime('%H:%M')

        # צור מפה למעבר של אותו יום ושעה
        transit_chart = Chart(Datetime(date_str, time_str, '+02:00'), BIRTH_LOCATION)
        moon = transit_chart.get(const.MOON)

        # בדוק אספקטים בין הירח לבין כוכבים חשובים במפת הלידה
        targets = [const.SUN, const.VENUS, const.JUPITER]
        for target in targets:
            natal_obj = birth_chart.get(target)

            # חשב את האספקט בין הירח לכוכב היעד
            aspect = aspects.getAspect(moon, natal_obj, [const.TRINE, const.SEXTILE])
            if aspect and aspect.type in [const.TRINE, const.SEXTILE]:
                retro_note = ' (🔁 נסיגה)' if natal_obj.retro else ''
                lucky_hours.append(f"{time_str} – {aspect.type} ל־{target}{retro_note}")
                break  # אם מצאנו – לא נבדוק עוד כוכבים בשעה הזו

    return lucky_hours
