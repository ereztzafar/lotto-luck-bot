import os
from datetime import datetime, timedelta
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const, angle
import pytz
import pandas as pd

# === פרטי לידה ===
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
TIMEZONE = '+02:00'
LOCATION = GeoPos('32n5', '34e53')  # פתח תקווה

# === כוכבים רלוונטיים ===
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]
ALL_OBJECTS = PLANETS + ['FORTUNE']
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MOON, const.PLUTO, 'FORTUNE']
HARMONIC_ANGLES = [0, 60, 120, 180]

# === שעות לבדיקה ביום ===
START_HOUR = 5
END_HOUR = 23
INTERVAL = 3

def calculate_part_of_fortune(chart):
    asc = chart.get(const.ASC).lon
    moon = chart.get(const.MOON).lon
    sun = chart.get(const.SUN).lon
    return angle.norm(asc + moon - sun)

def create_chart(date_str, time_str):
    dt = Datetime(date_str, time_str, TIMEZONE)
    return Chart(dt, LOCATION, IDs=PLANETS)

def calc_angle(pos1, pos2):
    diff = abs(pos1 - pos2) % 360
    return min(diff, 360 - diff)

def classify_score(score):
    if score >= 25:
        return '🟩 חזק'
    elif score >= 15:
        return '🟨 בינוני'
    elif score >= 1:
        return '🟧 מעניין'
    else:
        return '⬜ חלש מאוד'

def find_lucky_hours_for_day(date_obj, birth_chart, fortune_birth):
    date_str = date_obj.strftime('%Y/%m/%d')
    lucky_hours = []

    for hour in range(START_HOUR, END_HOUR + 1, INTERVAL):
        time_str = f"{hour:02d}:00"
        transit_chart = create_chart(date_str, time_str)
        fortune_now = calculate_part_of_fortune(transit_chart)

        score = 0
        for p1 in ALL_OBJECTS:
            pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
            for p2 in ALL_OBJECTS:
                pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
                ang_val = calc_angle(pos1, pos2)
                for h_angle in HARMONIC_ANGLES:
                    if abs(ang_val - h_angle) <= 4:
                        if p1 in MONEY_OBJECTS and p2 in MONEY_OBJECTS:
                            score += 1

        if score >= 1:
            lucky_hours.append({
                'שעה': time_str,
                'רמה': classify_score(score),
                'זוויות': score
            })

    return lucky_hours

def forecast_30_days():
    base_date = datetime.now(pytz.timezone("Asia/Jerusalem"))
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)
    days = []

    for i in range(30):
        day = base_date + timedelta(days=i)
        lucky = find_lucky_hours_for_day(day, birth_chart, fortune_birth)
        days.append({
            'תאריך': day.strftime('%Y-%m-%d'),
            'שעות מזל': lucky if lucky else '❌ ללא שעות טובות'
        })
    return days

# הפעלת התחזית
if __name__ == '__main__':
    forecast_result = forecast_30_days()
    rows = []
    for day in forecast_result:
        if isinstance(day['שעות מזל'], str):
            rows.append({
                'תאריך': day['תאריך'],
                'שעה': '',
                'רמה': day['שעות מזל'],
                'מספר זוויות': ''
            })
        else:
            for item in day['שעות מזל']:
                rows.append({
                    'תאריך': day['תאריך'],
                    'שעה': item['שעה'],
                    'רמה': item['רמה'],
                    'מספר זוויות': item['זוויות']
                })
    df = pd.DataFrame(rows)
    df.to_excel("lucky_hours_30_days.xlsx", index=False)
    print("✅ נשמר הקובץ: lucky_hours_30_days.xlsx")
