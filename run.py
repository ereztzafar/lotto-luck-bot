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

# ----------- טווח שעות בדיקה ----------
START_HOUR = 5
END_HOUR = 23
INTERVAL = 4  # כל 4 שעות

# ----------- כוכבים עיקריים ----------
PLANETS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
           const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]

# ----------- זוויות חשובות ----------
HARMONIC_ANGLES = [0, 60, 120, 180]
CHALLENGING_ANGLES = [90, 150]


def is_retrograde(chart, planet):
    return chart.get(planet).isRetrograde()


def format_pos(obj):
    deg = int(obj.lon)
    min = int((obj.lon - deg) * 60)
    sec = int(((obj.lon - deg) * 60 - min) * 60)
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
        return '🟩 יום חזק'
    elif score >= 15:
        return '🟨 יום בינוני'
    else:
        return '🟥 יום חלש'


def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסר TELEGRAM_TOKEN או CHAT_ID")
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')


def analyze_today():
    today = datetime.date.today().strftime('%Y/%m/%d')
    message = f"📆 <b>תחזית אסטרולוגית יומית – {today}</b>\n"
    message += f"🧬 תאריך לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n🕰️ בדיקת שעות מזל בין {START_HOUR}:00–{END_HOUR}:00\n\n"

    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    transit_now = create_chart(today, '12:00')

    # ---------- כוכבי לידה מול טרנזיט ----------
    message += "🌌 <b>כוכבי לידה מול טרנזיט:</b>\n"
    found_aspect = False
    for p1 in PLANETS:
        obj1 = birth_chart.get(p1)
        pos1 = obj1.lon
        for p2 in PLANETS:
            obj2 = transit_now.get(p2)
            pos2 = obj2.lon
            angle = calc_angle(pos1, pos2)
            if any(abs(angle - a) <= 6 for a in HARMONIC_ANGLES + CHALLENGING_ANGLES):
                found_aspect = True
                if angle in HARMONIC_ANGLES:
                    symbol = "✅"
                elif angle in CHALLENGING_ANGLES:
                    symbol = "⚠️" if angle == 150 else "❌"
                else:
                    continue
                message += f"• {p1} {format_pos(obj1)} ↔ {p2} {format_pos(obj2)} — {int(angle)}° {symbol}\n"
    if not found_aspect:
        message += "• לא נמצאו זוויות בולטות היום.\n"
    message += "\n"

    # ---------- נסיגות ----------
    retro_birth = [p for p in PLANETS if is_retrograde(birth_chart, p)]
    retro_today = [p for p in PLANETS if is_retrograde(transit_now, p)]
    message += "🔁 <b>כוכבים בנסיגה:</b>\n"
    message += f"• בלידה: {', '.join([p + ' ℞' for p in retro_birth])}\n"
    message += f"• היום: {', '.join([p + ' ℞' for p in retro_today])}\n"
    common = set(retro_birth) & set(retro_today)
    if common:
        message += f"✅ <i>השפעה חיובית אפשרית: {', '.join(common)}</i>\n\n"
    else:
        message += "\n"

    # ---------- שעות מזל ----------
    message += "🕰️ <b>שעות מזל מומלצות:</b>\n"
    lucky_times = []
    for hour in range(START_HOUR, END_HOUR + 1, INTERVAL):
        h_str = f"{hour:02d}:00"
        transit = create_chart(today, h_str)
        score = 0
        for p1 in PLANETS:
            for p2 in PLANETS:
                angle = calc_angle(birth_chart.get(p1).lon, transit.get(p2).lon)
                if any(abs(angle - a) <= 6 for a in HARMONIC_ANGLES):
                    score += 1
        level = classify_score(score)
        if score >= 15:
            lucky_times.append((h_str, score))
        message += f"• {h_str} – {level} ({score} נק')\n"

    if lucky_times:
        message += "\n🎯 <b>מומלץ למלא לוטו בין:</b>\n"
        for t, s in lucky_times:
            message += f"<b>{t}–{int(t[:2]) + 0:02d}:59</b> 🟢\n"
    else:
        message += "\n❌ אין שעות מזל חזקות היום.\n"

    # ---------- שליחה ----------
    send_telegram_message(message)


if __name__ == "__main__":
    analyze_today()
