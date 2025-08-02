import datetime
import os
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from math import fabs
import telegram

# ----------- טלגרם ----------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ----------- פרטי לידה ----------
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
LOCATION = GeoPos('32n5', '34e53')  # פתח תקווה
TIMEZONE = '+02:00'

# ----------- טווח שעות ----------
INTERVAL = 3  # כל שעתיים
DURATION_HOURS = 24  # סריקה ל-24 שעות קדימה

# ----------- כוכבים עיקריים ----------
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]

# ----------- זוויות חשובות ----------
HARMONIC_ANGLES = [0, 60, 120, 180]
CHALLENGING_ANGLES = [90, 150]

# ----------- פירושים לזוויות ----------
ASPECT_MEANINGS = {
    0: "צמידות – מיקוד ועוצמה חזקה",
    60: "שישית – הזדמנות חיובית, קלות",
    90: "ריבוע – אתגר, קונפליקט",
    120: "משולש – זרימה, הרמוניה",
    150: "קווינקונקס – חוסר נוחות, התאמה נדרשת",
    180: "אופוזיציה – מתח בין הפכים"
}

def calc_angle(pos1, pos2):
    angle = fabs(pos1 - pos2) % 360
    return min(angle, 360 - angle)

def create_chart(date_str, time_str):
    dt = Datetime(date_str, time_str, TIMEZONE)
    return Chart(dt, LOCATION, IDs=PLANETS)

def classify_score(score):
    if score >= 25:
        return '🟩 שעה חזקה'
    elif score >= 15:
        return '🟨 שעה בינונית'
    else:
        return '🟥 שעה חלשה'

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסר TELEGRAM_TOKEN או CHAT_ID")
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')

def analyze_next_24_hours():
    now = datetime.datetime.now()
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)

    message = f"📆 <b>תחזית 24 שעות הקרובות – {now.strftime('%d/%m/%Y %H:%M')}</b>\n"
    message += f"🧬 תאריך לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n\n"

    lucky_times = []

    current_dt = now.replace(minute=0, second=0, microsecond=0)
    end_dt = current_dt + datetime.timedelta(hours=DURATION_HOURS)

    while current_dt <= end_dt:
        date_str = current_dt.strftime('%Y/%m/%d')
        time_str = current_dt.strftime('%H:%M')
        transit = create_chart(date_str, time_str)

        score = 0
        details = ""

        for p1 in PLANETS:
            for p2 in PLANETS:
                angle = calc_angle(birth_chart.get(p1).lon, transit.get(p2).lon)
                for target in HARMONIC_ANGLES:
                    if abs(angle - target) <= 6:
                        score += 1
                        break  # סופר רק זווית אחת בין כל זוג כוכבים

        level = classify_score(score)
        message += f"• {date_str} {time_str} – {level} ({score} נק')\n"
        if score >= 15:
            lucky_times.append((current_dt, score))

        current_dt += datetime.timedelta(hours=INTERVAL)

    if lucky_times:
        message += "\n🎯 <b>שעות מומלצות למילוי לוטו:</b>\n"
        for dt, score in sorted(lucky_times, key=lambda x: -x[1]):
            end_time = dt + datetime.timedelta(hours=INTERVAL)
            message += f"{dt.strftime('%d/%m %H:%M')}–{end_time.strftime('%H:%M')} 🟢 ({score} נק')\n"
    else:
        message += "\n❌ לא נמצאו שעות מזל חזקות ב־24 השעות הקרובות.\n"

    send_telegram_message(message)

if __name__ == "__main__":
    analyze_next_24_hours()
