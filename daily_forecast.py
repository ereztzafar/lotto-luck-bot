from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

import datetime

# מיקום הלידה הקבוע שלך (פתח תקווה)
BIRTH_LOCATION = GeoPos("32n5", "34e53")  # פתח תקווה לפי פורמט flatlib

def find_lucky_hours(birth_chart, current_chart):
    """
    משווה בין מפת הלידה למפת הטרנזיט ומחזירה שעות מומלצות למילוי לוטו.
    התנאי הראשוני: ירח ב־Trine / Sextile לשמש, ונוס, צדק.
    """
    lucky_hours = []

    # כוכבים נבחרים לבדיקה
    natal_moon = birth_chart.get(const.MOON)

    now = datetime.datetime.now()

    # בדיקת כל שעתיים היום (מ־05:00 עד 23:00)
    for hour in range(5, 24, 2):
        forecast_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        date_str = forecast_time.strftime('%Y/%m/%d')  # ✅ תיקון פורמט התאריך
        time_str = forecast_time.strftime('%H:%M')

        transit_chart = Chart(Datetime(date_str, time_str, '+02:00'), BIRTH_LOCATION)

        moon = transit_chart.get(const.MOON)
        aspects = moon.aspectList([birth_chart.get(const.SUN),
                                    birth_chart.get(const.VENUS),
                                    birth_chart.get(const.JUPITER)])

        # סינון היבטים חיוביים בלבד
        for asp in aspects:
            if asp.type in [const.TRINE, const.SEXTILE]:
                lucky_hours.append(f"{time_str} – {asp.type} ל־{asp.obj}")
                break  # מספיק היבט חיובי אחד

    return lucky_hours
