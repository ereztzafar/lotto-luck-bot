import os
import datetime
import pytz
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib import angle
from flatlib.geopos import GeoPos
from flatlib import const
from flatlib import aspects
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
INTERVAL = 3

# === כוכבים רלוונטיים ===
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]
ALL_OBJECTS = PLANETS + ['FORTUNE']

# === כוכבים שקשורים לכסף ===
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MOON, const.PLUTO, 'FORTUNE']

# === זוויות חשובות ===
HARMONIC_ANGLES = [0, 60, 120, 180]
CHALLENGING_ANGLES = []

ASPECT_MEANINGS = {
    0: "צמידות – מיקוד ועוצמה חזקה",
    60: "שישית – הזדמנות חיובית, קלות",
    90: "ריבוע – אתגר, קונפליקט",
    120: "משולש – זרימה, הרמוניה",
    
}

# === מזלות לפי מעלות גלגל המזלות ===
SIGNS = [
    'ARIES', 'TAURUS', 'GEMINI', 'CANCER', 'LEO', 'VIRGO',
    'LIBRA', 'SCORPIO', 'SAGITTARIUS', 'CAPRICORN', 'AQUARIUS', 'PISCES'
]

def calculate_part_of_fortune(chart):
    # פורטונה ביום: ASC + ירח - שמש
    asc = chart.get(const.ASC).lon
    moon = chart.get(const.MOON).lon
    sun = chart.get(const.SUN).lon
    fortune = angle.norm(asc + moon - sun)
    return fortune

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
    return Chart(dt, LOCATION, IDs=PLANETS)

def classify_score(score):
    if score >= 25:
        return '🟩 יום חזק'
    elif score >= 15:
        return '🟨 יום בינוני'
    else:
        return '🟥 יום חלש'

def estimate_time_range(angle_value):
    return "08:00–14:00"

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
    fortune_sign = get_sign(fortune_birth)
    fortune_deg = int(fortune_birth % 30)
    fortune_min = int((fortune_birth % 1) * 60)

    message = f"📆 <b>תחזית אסטרולוגית ל־24 שעות הקרובות – {now.strftime('%Y/%m/%d %H:%M')}</b>\n"
    message += f"🧬 תאריך לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n"
    message += f"🌠 <b>פורטונה בלידה</b>: {fortune_sign} {fortune_deg}°{fortune_min:02d}′\n"
    message += f"🕰️ שעות נבדקות: {current_hour:02d}:00–{END_HOUR}:00\n\n"

    today = now.strftime('%Y/%m/%d')
    transit_noon = create_chart(today, '12:00')
    fortune_transit = calculate_part_of_fortune(transit_noon)

    # === זוויות בין כוכבי לידה לטרנזיט ===
    message += "🌌 <b>זוויות בין כוכבי לידה לטרנזיט:</b>\n"
    aspects_found = False
    for p1 in PLANETS:
        obj1 = birth_chart.get(p1)
        for p2 in PLANETS:
            obj2 = transit_noon.get(p2)
            angle_val = calc_angle(obj1.lon, obj2.lon)
            for target_angle in HARMONIC_ANGLES + CHALLENGING_ANGLES:
                if abs(angle_val - target_angle) <= 8:
                    symbol = "✅" if target_angle in HARMONIC_ANGLES else "⚠️" if target_angle == 150 else "❌"
                    meaning = ASPECT_MEANINGS.get(target_angle, "")
                    time_range = estimate_time_range(target_angle)
                    message += (f"🔹 <b>{p1}</b> {format_position(obj1)} ↔ <b>{p2}</b> {format_position(obj2)} — "
                                f"{int(angle_val)}° {symbol}\n• {meaning} | 🕒 {time_range}\n")
                    aspects_found = True
                    break
    if not aspects_found:
        message += "• לא נמצאו זוויות בולטות.\n"
    message += "\n"

    # === נסיגות ===
    retro_birth = [p for p in PLANETS if birth_chart.get(p).isRetrograde()]
    retro_now = [p for p in PLANETS if transit_noon.get(p).isRetrograde()]
    message += "🔁 <b>כוכבים בנסיגה:</b>\n"
    message += f"• בלידה: {', '.join(p + ' ℞' for p in retro_birth) or 'ללא'}\n"
    message += f"• היום: {', '.join(p + ' ℞' for p in retro_now) or 'ללא'}\n"
    common = set(retro_birth) & set(retro_now)
    if common:
        message += f"✅ <i>השפעה חוזרת: {', '.join(common)}</i>\n"
    message += "\n"

    # === שעות מזל ===
    message += "🕰️ <b>שעות מזל:</b>\n"
    lucky_hours = []

    for hour in range(max(now.hour, START_HOUR), END_HOUR + 1):
        time_str = f"{hour:02d}:00"
        transit_chart = create_chart(today, time_str)
        fortune_now = calculate_part_of_fortune(transit_chart)

        score = 0
        highlights = []

        for p1 in PLANETS + ['FORTUNE']:
            pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
            for p2 in PLANETS + ['FORTUNE']:
                pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
                ang_val = calc_angle(pos1, pos2)
                for h_angle in HARMONIC_ANGLES:
                    if abs(ang_val - h_angle) <= 8:
                        if p1 in MONEY_OBJECTS and p2 in MONEY_OBJECTS:
                            score += 1
                            money_tag = '💰'
                            fortuna_tag = '🎯' if 'FORTUNE' in [p1, p2] else ''
                            highlights.append(f"🔸 {p1} {money_tag}{fortuna_tag} ↔ {p2} {money_tag}{fortuna_tag} – {int(ang_val)}°")
                            break



        level = classify_score(score)
        message += f"• {time_str} – {level} ({score} נק')\n"
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
        message += "\n❌ אין שעות מזל משמעותיות היום.\n"

    send_telegram_message(message)


if __name__ == '__main__':
    analyze_today()
