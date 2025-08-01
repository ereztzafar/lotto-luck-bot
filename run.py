import datetime
import os
import requests
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const, aspects
from math import fabs

# ---------- טלגרם ----------
import telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ---------- פרטי לידה ----------
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
LOCATION = GeoPos('32n5', '34e53')  # פתח תקווה

# ---------- טווח שעות בדיקה ----------
START_HOUR = 5
END_HOUR = 23


# ---------- כוכבים הקשורים לכסף בלבד ----------
PLANETS = [const.MOON, const.VENUS, const.JUPITER, const.PLUTO]


# ---------- זוויות הרמוניות (במעלות) ----------
HARMONIC_ANGLES = [0, 60, 120, 180]


# ---------- בדיקת נסיגה ----------
def is_retrograde(chart, planet):
    return chart.get(planet).retrograde


# ---------- חישוב זווית בין שני כוכבים ----------
def calc_angle(pos1, pos2):
    angle = fabs(pos1 - pos2) % 360
    return min(angle, 360 - angle)


# ---------- קבלת דירוג הרמוני ----------
def harmony_score(birth_chart, transit_chart):
    score = 0
    for p1 in PLANETS:
        for p2 in PLANETS:
            angle = calc_angle(
                birth_chart.get(p1).lon, transit_chart.get(p2).lon)
            if any(fabs(angle - a) < 6 for a in HARMONIC_ANGLES):
                score += 1
    return score


# ---------- דירוג מילולי ----------
def classify_score(score):
    if score >= 10:
        return '🟩 יום חזק'
    elif score >= 5:
        return '🟨 יום בינוני'
    else:
        return '🟥 יום חלש'


# ---------- יצירת מפת אסטרולוגיה ----------
def create_chart(date_str, time_str, location):
    dt = Datetime(date_str, time_str, '+02:00')
    return Chart(dt, location)


# ---------- שליחת הודעה לטלגרם ----------
def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסר TELEGRAM_TOKEN או CHAT_ID")
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')


# ---------- הרצת ניתוח יומי ----------
def analyze_today():
    today = datetime.date.today().strftime('%Y/%m/%d')
    message = f"🔮 תחזית אסטרולוגית להיום {today}:\n"

    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME, LOCATION)

    lucky_hours = []

    for hour in range(START_HOUR, END_HOUR + 1):
        hour_str = f"{hour:02d}:00"
        transit_chart = create_chart(today, hour_str, LOCATION)
        score = harmony_score(birth_chart, transit_chart)

        if score >= 5:
            lucky_hours.append((hour_str, score))

    # שליחת נסיגות
    retrogrades = [p for p in PLANETS if is_retrograde(
        create_chart(today, '12:00', LOCATION), p)]
    if retrogrades:
        message += "\n🔁 <b>כוכבים בנסיגה:</b>\n"
        for r in retrogrades:
            message += f"• {r}\n"
    else:
        message += "\n✅ אין כוכבים בנסיגה.\n"

    # שעות מזל
    if lucky_hours:
        message += "\n🕰️ <b>שעות מזל מומלצות:</b>\n"
        for hour, score in lucky_hours:
            level = classify_score(score)
            message += f"• {hour} – {level} ({score} נק')\n"
    else:
        message += "\n❌ אין שעות מזל חזקות היום.\n"

    # שליחה לטלגרם
    send_telegram_message(message)


# ---------- הפעלה ----------
if __name__ == "__main__":
    analyze_today()

