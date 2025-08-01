from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime

# מיקום הלידה הקבוע שלך (פתח תקווה)
BIRTH_LOCATION = GeoPos("32n5", "34e53")  # פתח תקווה לפי פורמט flatlib

def find_lucky_hours(birth_chart, current_chart):
    """
    משווה בין מפת הלידה למפת הטרנזיט ומחזירה שעות מזל להגרלות (לוטו, חישגד, צ'אנס).
    נבדק היבט חיובי של הירח מול שמש/ונוס/צדק – אם אין נסיגה שפוגעת באיכות.
    """
    lucky_hours = []
    now = datetime.datetime.now()

    # בדיקת כל שעתיים היום (מ־05:00 עד 23:00)
    for hour in range(5, 24, 2):
        forecast_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        date_str = forecast_time.strftime('%Y/%m/%d')  # פורמט נכון ל־Flatlib
        time_str = forecast_time.strftime('%H:%M')

        transit_chart = Chart(Datetime(date_str, time_str, '+02:00'), BIRTH_LOCATION)
        moon = transit_chart.get(const.MOON)

        # בדיקת היבטים חיוביים מול שמש, ונוס, צדק
        targets = [const.SUN, const.VENUS, const.JUPITER]
        for target in targets:
            natal_obj = birth_chart.get(target)
            aspects = moon.aspectList([natal_obj])

            for asp in aspects:
                if asp.type in [const.TRINE, const.SEXTILE]:
                    retro_note = ' (🔁 נסיגה)' if natal_obj.retro else ''
                    lucky_hours.append(f"{time_str} – {asp.type} ל־{target}{retro_note}")
                    break  # מספיק היבט חיובי אחד

    return lucky_hours
