from flatlib import const, aspects
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime

# מיקום הלידה שלך (פתח תקווה)
BIRTH_LOCATION = GeoPos("32n5", "34e53")

# אספקטים חיוביים בלבד
POSITIVE_ASPECTS = [const.CONJUNCTION, const.SEXTILE, const.TRINE]

# תרגום לעברית לאספקטים
ASPECT_TRANSLATIONS = {
    const.CONJUNCTION: "צמידות",
    const.SEXTILE: "שישון",
    const.SQUARE: "ריבוע",
    const.TRINE: "שלישון",
    const.OPPOSITION: "התנגדות"
}

# כל הכוכבים האפשריים במפת לידה
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]

def find_lucky_hours(birth_chart, current_chart):
    lucky_hours = []
    now = datetime.datetime.now()

    for hour in range(5, 24, 2):  # בין 05:00 ל־22:00 כל שעתיים
        forecast_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        date_str = forecast_time.strftime('%Y/%m/%d')
        time_str = forecast_time.strftime('%H:%M')

        # צור מפה לטרנזיט
        transit_chart = Chart(Datetime(date_str, time_str, '+02:00'), BIRTH_LOCATION)
        moon = transit_chart.get(const.MOON)

        for target in PLANETS:
            natal_obj = birth_chart.get(target)
            aspect = aspects.getAspect(moon, natal_obj)

            if aspect and aspect.type in POSITIVE_ASPECTS:
                aspect_name = ASPECT_TRANSLATIONS.get(aspect.type, aspect.type)
                retro_note = ' (🔁 נסיגה)' if natal_obj.retro else ''
                lucky_hours.append(f"{time_str} – {aspect_name} ל־{target}{retro_note}")
                break  # מספיק אספקט חיובי אחד בשעה הזו

    return lucky_hours
