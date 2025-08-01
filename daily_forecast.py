from flatlib import const, aspects
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime

# מיקום הלידה הקבוע שלך (פתח תקווה)
BIRTH_LOCATION = GeoPos("32n5", "34e53")  # פתח תקווה לפי פורמט flatlib

def find_lucky_hours(birth_chart, current_chart):
    from flatlib import const

    lucky_hours = []
    now = datetime.datetime.now()

    for hour in range(5, 24, 2):
        forecast_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        date_str = forecast_time.strftime('%Y/%m/%d')
        time_str = forecast_time.strftime('%H:%M')

        transit_chart = Chart(Datetime(date_str, time_str, '+02:00'), BIRTH_LOCATION)
        moon = transit_chart.get(const.MOON)

        targets = [const.SUN, const.VENUS, const.JUPITER]
        for target in targets:
            natal_obj = birth_chart.get(target)
            aspects_list = moon.aspectList([natal_obj])

            for asp in aspects_list:
                if asp.type in [const.TRINE, const.SEXTILE]:
                    retro_note = ' (🔁 נסיגה)' if natal_obj.retro else ''
                    lucky_hours.append(f"{time_str} – {asp.type} ל־{target}{retro_note}")
                    break

    return lucky_hours
