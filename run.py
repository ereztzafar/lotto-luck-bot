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

# ----------- טווח שעות קדימה ----------
HOURS_FORWARD = 24
INTERVAL = 2  # קפיצה כל שעתיים

# ----------- כוכבים עיקריים ----------
PLANETS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
           const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]

# ----------- זוויות חשובות ----------
HARMONIC_ANGLES = [0, 60, 120, 180]
CHALLENGING_ANGLES = [90, 150]

ASPECT_MEANINGS = {
    0: "צמידות – מיקוד ועוצמה חזקה",
    60: "שישית – הזדמנות חיובית, קלות",
    90: "ריבוע – אתגר, קונפליקט",
    120: "משולש – זרימה, הרמוניה",
    150: "קווינקונקס – חוסר נוחות, התאמה נדרשת",
    180: "אופוזיציה – מתח בין הפכים"
}

def is_retrograde(chart, planet):
    return chart.get(planet).isRetrograde()

def format_pos(obj):
    lon = obj.lon % 360
    deg = int(lon)
    minutes_float = (lon - deg) * 60
    min = int(minutes_float)
    sec = int((minutes_float - min) * 60)
    retro = " ℞" if obj.isRetrograde() else ""
    return f"{obj.sign} {deg}°{min:02d}′{sec:02d}″{retro}"

def calc_angle(pos1, pos2):
    angle = fabs(pos1 - pos2) % 360
    return min(angle, 360 - angle)

def create_chart(date_str, time_str):
    dt = Datetime(date_str, time_str, TIMEZONE)
    return Chart(dt, LOCATION, IDs=PLANETS)

def classify_score(score):
    if score >= 25:
        return '🟩 חזק מאוד'
    elif score >= 15:
        return '🟨 בינוני'
    elif score >= 8:
        return '🟧 קל'
    else:
        return '⬜ חלש'

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסר TELEGRAM_TOKEN או CHAT_ID")
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')

def analyze_next_24h():
    now = datetime.datetime.now()
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    
    message = f"📆 <b>תחזית אסטרולוגית – {now.strftime('%d/%m/%Y')}</b>\n"
    message += f"🧬 תאריך לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n"
    message += f"⏳ טווח: {HOURS_FORWARD} שעות קדימה כל {INTERVAL} שעות\n\n"
    message += "🕰️ <b>שעות מזל:</b>\n"

    lucky_slots = []

    for hour_offset in range(0, HOURS_FORWARD + 1, INTERVAL):
        time_point = now + datetime.timedelta(hours=hour_offset)
        date_str = time_point.strftime('%Y/%m/%d')
        time_str = time_point.strftime('%H:%M')
        chart = create_chart(date_str, time_str)

        score = 0
        details = []
        for p1 in PLANETS:
            obj1 = birth_chart.get(p1)
            for p2 in PLANETS:
                obj2 = chart.get(p2)
                angle = calc_angle(obj1.lon, obj2.lon)
                for target_angle in HARMONIC_ANGLES + CHALLENGING_ANGLES:
                    if abs(angle - target_angle) <= 6:
                        score += 1
                        symbol = "✅" if target_angle in HARMONIC_ANGLES else "⚠️" if target_angle == 150 else "❌"
                        meaning = ASPECT_MEANINGS.get(target_angle, "")
                        details.append(f"{p1} ↔ {p2} – {int(angle)}° {symbol} ({meaning})")
                        break

        level = classify_score(score)
        message += f"• {time_point.strftime('%H:%M')} – {level} ({score} זוויות)\n"
        if score >= 15:
            lucky_slots.append((time_point.strftime('%H:%M'), score, details))

    if lucky_slots:
        message += "\n🎯 <b>שעות לוטו חזקות:</b>\n"
        for h, s, _ in lucky_slots:
            message += f"🟢 <b>{h}</b> ({s} זוויות חיוביות)\n"
    else:
        message += "\n❌ לא נמצאו שעות חזקות במיוחד.\n"

    message += "\n🌀 <b>נסיגות:</b>\n"
    now_str = now.strftime('%Y/%m/%d %H:%M')
    chart_now = create_chart(now_str.split()[0], now_str.split()[1])
    retro_birth = [p for p in PLANETS if is_retrograde(birth_chart, p)]
    retro_today = [p for p in PLANETS if is_retrograde(chart_now, p)]
    message += f"• בלידה: {', '.join(p + ' ℞' for p in retro_birth) or 'ללא'}\n"
    message += f"• עכשיו: {', '.join(p + ' ℞' for p in retro_today) or 'ללא'}\n"
    common = set(retro_birth) & set(retro_today)
    if common:
        message += f"✅ השפעה חוזרת: {', '.join(common)}\n"

    send_telegram_message(message)

if __name__ == "__main__":
    analyze_next_24h()
