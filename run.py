import os
from datetime import datetime, timedelta
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const, angle
import pytz
import telegram

# === טלגרם ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === פרטי לידה ===
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
TIMEZONE = '+02:00'
LOCATION = GeoPos('32n5', '34e53')  # פתח תקווה

# === כוכבים והשפעות ===
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]
ALL_OBJECTS = PLANETS + ['FORTUNE']
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MOON, const.PLUTO, 'FORTUNE']
HARMONIC_ANGLES = [0, 60, 120, 180]

# === הגדרות זמן סריקה בכל יום ===
START_HOUR = 5
END_HOUR = 23
INTERVAL = 3

# === חישובי עזר ===
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

# === חישוב שעות מזל ליום מסוים ===
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
            lucky_hours.append(f"{time_str} – {classify_score(score)} ({score} זוויות)")

    return lucky_hours

# === שליחת הודעה לטלגרם ===
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסרים TELEGRAM_TOKEN או CHAT_ID בסביבה")
        return
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for part in chunks:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=part, parse_mode='HTML')
    except Exception as e:
        print(f"שגיאה בשליחה לטלגרם: {e}")

# === תחזית 30 ימים ===
def forecast_and_send():
    now = datetime.now(pytz.timezone("Asia/Jerusalem"))
    base_date = now
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)

    message = f"📆 <b>תחזית שעות מזל ל־30 הימים הקרובים</b>\n"
    message += f"🧬 לפי מפת לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n"
    message += f"🎯 כל שעה שבה אפילו כוכב אחד תומך בלוטו – תוצג כאן.\n\n"

    for i in range(30):
        day = base_date + timedelta(days=i)
        lucky_hours = find_lucky_hours_for_day(day, birth_chart, fortune_birth)
        message += f"📅 <b>{day.strftime('%Y-%m-%d')}</b>\n"
        if lucky_hours:
            for hour in lucky_hours:
                message += f"• {hour}\n"
        else:
            message += "❌ ללא שעות טובות\n"
        message += "\n"

    send_telegram(message)

# === הפעלה
if __name__ == '__main__':
    forecast_and_send()
