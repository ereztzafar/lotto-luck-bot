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

# === פרטי לידה שלך ===
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
TIMEZONE = '+02:00'
LOCATION = GeoPos('32n5', '34e53')  # פתח תקווה

# === כוכבים רלוונטיים למזל פיננסי ===
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]
ALL_OBJECTS = PLANETS + ['FORTUNE']
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MOON, const.PLUTO, 'FORTUNE']
HARMONIC_ANGLES = [0, 60, 120, 180]

# === טווח שעות כל יום ===
START_HOUR = 5
END_HOUR = 23
INTERVAL = 3

# === מיפוי סמלים לכוכבים ===
PLANET_ICONS = {
    const.SUN: "☀️", const.MOON: "🌙", const.MERCURY: "☿", const.VENUS: "♀",
    const.MARS: "♂", const.JUPITER: "♃", const.SATURN: "♄", const.URANUS: "♅",
    const.NEPTUNE: "♆", const.PLUTO: "♇", 'FORTUNE': "🎯"
}

ANGLE_MEANINGS = {
    0: "צמידות חדה",
    60: "הזדמנות שקטה",
    120: "זרימה כספית",
    180: "הפתעה פתאומית"
}

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

def estimate_potential_score(n):
    if n >= 9:
        return "🟢🟢 95–100%"
    elif n >= 7:
        return "🟢 85–94%"
    elif n >= 5:
        return "🟢 70–84%"
    elif n >= 3:
        return "🟡 50–69%"
    elif n >= 1:
        return "🔘 30–49%"
    else:
        return "⬜ 0%"

def find_lucky_hours(date_obj, birth_chart, fortune_birth):
    date_str = date_obj.strftime('%Y/%m/%d')
    lucky_blocks = []

    for hour in range(START_HOUR, END_HOUR + 1, INTERVAL):
        time_str = f"{hour:02d}:00"
        transit_chart = create_chart(date_str, time_str)
        fortune_now = calculate_part_of_fortune(transit_chart)

        found_aspects = []
        for p1 in MONEY_OBJECTS:
            pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
            for p2 in MONEY_OBJECTS:
                pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
                ang_val = calc_angle(pos1, pos2)
                for h_angle in HARMONIC_ANGLES:
                    if abs(ang_val - h_angle) <= 3:
                        icon1 = PLANET_ICONS.get(p1, p1)
                        icon2 = PLANET_ICONS.get(p2, p2)
                        meaning = ANGLE_MEANINGS.get(h_angle, "")
                        found_aspects.append(f"{icon1} {p1} ↔ {icon2} {p2} — {h_angle}° {meaning}")
        if found_aspects:
            lucky_blocks.append({
                'שעה': time_str,
                'זוויות': found_aspects
            })
    return lucky_blocks

def send_telegram_message(message: str):
    """שליחה בטוחה לטלגרם:
    - חיתוך לפי בתים (UTF-8) עד ~4000
    - בלי parse_mode כדי לא לשבור תגיות
    - נפילה חכמה לשליחת קובץ אם עדיין ארוך מדי
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסר TELEGRAM_TOKEN או CHAT_ID")
        return

    import io
    MAX_BYTES = 4000  # שמרני (4096 הוא המקסימום של טלגרם)

    def chunk_by_bytes(text: str, max_bytes: int):
        parts, buf = [], bytearray()
        for line in text.splitlines(True):  # כולל התו \n
            b = line.encode("utf-8")
            if len(b) > max_bytes:
                # חותכים גם שורה בודדת אם היא לבדה חורגת
                start = 0
                while start < len(b):
                    room = max_bytes - len(buf)
                    if room == 0:
                        parts.append(buf.decode("utf-8", "ignore"))
                        buf = bytearray()
                        room = max_bytes
                    take = min(room, len(b) - start)
                    buf.extend(b[start:start+take])
                    start += take
                    if len(buf) == max_bytes:
                        parts.append(buf.decode("utf-8", "ignore"))
                        buf = bytearray()
            else:
                if len(buf) + len(b) > max_bytes:
                    parts.append(buf.decode("utf-8", "ignore"))
                    buf = bytearray()
                buf.extend(b)
        if buf:
            parts.append(buf.decode("utf-8", "ignore"))
        return parts

    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        for part in chunk_by_bytes(message, MAX_BYTES):
            # בלי parse_mode כדי להימנע משגיאת entities כשהמקטע נחתך
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=part)
    except Exception as e:
        print(f"שגיאת טלגרם בעת שליחה מפוצלת: {e}. שולח כקובץ…")
        try:
            bio = io.BytesIO(message.encode("utf-8"))
            bio.name = "forecast.txt"
            telegram.Bot(token=TELEGRAM_TOKEN).send_document(
                chat_id=TELEGRAM_CHAT_ID,
                document=bio,
                caption="ההודעה הייתה ארוכה – נשלחה כקובץ"
            )
        except Exception as ee:
            print(f"שגיאת טלגרם גם בשליחת קובץ: {ee}")


def build_and_send_forecast():
    tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(tz)
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)

    message = f"📆 <b>תחזית לוטו אסטרולוגית – 3 הימים הקרובים 🎟️</b>\n"
    message += f"🧬 לפי מפת לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n"
    message += f"🎯 שעות מזל כספי מוצגות לפי זוויות בין כוכבי לידה לטרנזיט:\n\n"

    for i in range(3):
        day = now + timedelta(days=i)
        date_str = day.strftime('%Y/%m/%d')
        message += f"📅 <b>{date_str}</b>\n"

        transit_chart_noon = create_chart(date_str, '12:00')
        retro_now = []
        for p in PLANETS:
            if transit_chart_noon.get(p).isRetrograde():
                retro_now.append(p)
        if retro_now:
            icons = [f"{PLANET_ICONS[p]} {p} ℞" for p in retro_now]
            message += f"🔁 <b>כוכבים בנסיגה:</b> " + ", ".join(icons) + "\n"
            if len(retro_now) >= 4:
                message += f"⚠️ <i>המלצה: לנקוט זהירות – השפעת נסיגות מרובה</i>\n"
        message += "\n"

        lucky_hours = find_lucky_hours(day, birth_chart, fortune_birth)
        if not lucky_hours:
            message += "❌ אין שעות מזל לוטו ביום זה.\n\n"
            continue
        for block in lucky_hours:
            num_aspects = len(block['זוויות'])
            percent = estimate_potential_score(num_aspects)
            message += f"🕐 <b>{block['שעה']}</b> – 💰 פוטנציאל זכייה: {percent}\n"
            for asp in block['זוויות']:
                message += f"• {asp}\n"
            message += "\n"

        best = max(lucky_hours, key=lambda x: len(x['זוויות']))['שעה']
        message += f"🟢 <i>המלצה: למלא לוטו,חישגד,צ'אנס סביב {best}</i>\n\n"

    send_telegram_message(message)

# === הפעלה
if __name__ == '__main__':
    build_and_send_forecast()
