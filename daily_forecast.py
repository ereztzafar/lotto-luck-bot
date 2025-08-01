from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

import datetime

# מיקום הלידה הקבוע שלך (פתח תקווה)
BIRTH_LOCATION = GeoPos("32n5", "34e53")  # פתח תקווה לפי פורמט flatlib

# טווח סטייה מקובל להיבטים (Orb)
ASPECT_ORB = 6

# פונקציית עזר לחישוב זווית בין שני כוכבים
def angle_between(lon1, lon2):
    angle = abs(lon1 - lon2) % 360
    return min(angle, 360 - angle)

# פונקציית עזר לבדוק אם הזווית תואמת להיבט רצוי
def is_positive_aspect(angle):
    return (
        abs(angle - 60) <= ASPECT_ORB or   # Sextile
        abs(angle - 120) <= ASPECT_ORB     # Trine
    )

def find_lucky_hours(birth_chart, current_chart):
    """
    משווה בין מפת הלידה למפת הטרנזיט ומחזירה שעות מומלצות למילוי לוטו.
    התנאי הראשוני: ירח ב־Trine / Sextile לשמש, ונוס, צדק.
    """
    lucky_hours = []

    # קבלת מיקומי שמש, ונוס וצדק ממפת הלידה
    natal_sun = birth_chart.get(const.SUN).lon
    natal_venus = birth_chart.get(const.VENUS).lon
    natal_jupiter = birth_chart.get(const.JUPITER).lon

    now = datetime.datetime.now()

    # בדיקת כל שעתיים היום (מ־05:00 עד 23:00)
    for hour in range(5, 24, 2):
        forecast_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        date_str = forecast_time.strftime('%Y/%m/%d')  # ✅ פורמט תקין ל־flatlib
        time_str = forecast_time.strftime('%H:%M')

        # מפת טרנזיט לשעה הנוכחית
        transit_chart = Chart(Datetime(date_str, time_str, '+02:00'), BIRTH_LOCATION)
        moon = transit_chart.get(const.MOON).lon

        # חישוב זוויות מול כל כוכב
        for target, name in [(natal_sun, "שמש"), (natal_venus, "ונוס"), (natal_jupiter, "צדק")]:
            angle = angle_between(moon, target)
            if is_positive_aspect(angle):
                lucky_hours.append(f"{time_str} – ירח בזווית {int(angle)}° ל־{name}")
                break  # מספיק היבט חיובי אחד לשעה זו

    return lucky_hours
