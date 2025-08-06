import os
import datetime
import pytz
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib import angle
from flatlib.geopos import GeoPos
from flatlib import const
from math import fabs
import telegram

# === טלגרם ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === פרטי לידה ===
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
TIMEZONE = '+02:00'
LOCATION = GeoPos('32n5', '34e53')  # פתח תקווה

# === הגדרות סריקה ===
START_HOUR = 5
END_HOUR = 23

# === רק כוכבים רלוונטיים לכסף ומזל ===
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MERCURY, const.MOON, const.PLUTO, 'FORTUNE']
HARMONIC_ANGLES = [60, 120]  # רק זוויות חיוביות
ANGLE_TOLERANCE = 4  # טווח סטייה בזווית

# === מזלות לפי מעלות גלגל המזלות ===
SIGNS = [
    'ARIES', 'TAURUS', 'GEMINI', 'CANCER', 'LEO', 'VIRGO',
    'LIBRA', 'SCORPIO', 'SAGITTARIUS', 'CAPRICORN', 'AQUARIUS', 'PISCES'
]

def calculate_part_of_fortune(chart):
    asc = chart.get(const.ASC).lon
    moon = chart.get(const.MOON).lon
    sun = chart.get(const.SUN).lon
    return angle.norm(asc + moon - sun)

def format_position(obj):
    lon = obj.lon % 360
    deg = int(lon)
    minutes = int((lon - deg) * 60)
    retro = " ℞" if obj.isRetrograde() else ""
    return f"{obj.sign} {deg}°{minutes:02d}′{retro}"

def calc_angle(pos1, pos2):
    diff = fabs(pos1 - pos2) % 360
    return min(diff, 360 - diff)

def get_sign(lon):
    index = int((lon % 360) / 30)
    return SIGNS[index]

def create_chart(date_str, time_str):
    dt = Datetime(date_str, time_str, TIMEZONE)
    # ודא ש־Sun כלול
    essential_ids = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]
    return Chart(dt, LOCATION, IDs=essential_ids)


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
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        max_length = 3000
        parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        for part in parts:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=part, parse_mode='HTML')
    except Exception as e:
        print(f"שגיאת טלגרם: {e}")

def analyze_today():
    tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.datetime.now(tz)
    current_hour = now.hour
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)

    today = now.strftime('%Y/%m/%d')
    message = f"📆 <b>תחזית מזל וכסף – {now.strftime('%Y/%m/%d %H:%M')}</b>\n"
    message += f"🌠 פורטונה בלידה: {get_sign(fortune_birth)} {int(fortune_birth % 30)}°{int((fortune_birth % 1) * 60):02d}′\n"
    message += f"🕰️ שעות נבדקות: {current_hour:02d}:00–{END_HOUR}:00\n\n"
    message += "🪙 <b>שעות מזל חזקות (כוכבים כספיים בלבד):</b>\n"

    lucky_hours = []

    for hour in range(max(current_hour, START_HOUR), END_HOUR + 1):
        time_str = f"{hour:02d}:00"
        transit_chart = create_chart(today, time_str)
        fortune_now = calculate_part_of_fortune(transit_chart)

        score = 0
        highlights = []

        for p1 in MONEY_OBJECTS:
            pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
            for p2 in MONEY_OBJECTS:
                pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
                ang_val = calc_angle(pos1, pos2)
                for h in HARMONIC_ANGLES:
                    if abs(ang_val - h) <= ANGLE_TOLERANCE:
                        score += 1
                        tag1 = '🎯' if p1 == 'FORTUNE' else '💰'
                        tag2 = '🎯' if p2 == 'FORTUNE' else '💰'
                        highlights.append(f"🔸 {p1} {tag1} ↔ {p2} {tag2} – {int(ang_val)}°")
                        break

        level = classify_score(score)
        message += f"• {time_str} – {level} ({score} זוויות חיוביות)\n"
        for line in highlights:
            message += f"   {line}\n"

        if score >= 15:
            lucky_hours.append((hour, score))

    if lucky_hours:
        message += "\n🎯 <b>המלצות מילוי לוטו:</b>\n"
        for hour, score in sorted(lucky_hours, key=lambda x: -x[1]):
            end = min(hour + 2, END_HOUR)
            message += f"<b>{hour:02d}:00–{end:02d}:00</b> 🟢 ({score} זוויות חיוביות)\n"
    else:
        message += "\n❌ אין שעות חזקות מספיק להמלצה.\n"

    send_telegram_message(message)

if __name__ == '__main__':
    analyze_today()
