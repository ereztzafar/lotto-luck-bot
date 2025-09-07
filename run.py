import os
import re
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
LOCATION = GeoPos('32n5', '34e53')  # פתח תקוה

# === כוכבים רלוונטיים למזל פיננסי ===
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]
ALL_OBJECTS = PLANETS + ['FORTUNE']
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MOON, const.PLUTO, 'FORTUNE']
HARMONIC_ANGLES = [0, 60, 120, 180]

# === טווח שעות כל יום לתחזית 3 ימים ===
START_HOUR = 1
END_HOUR = 24
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

# מדרג מילולי לתחזית 3 ימים (לפי מספר זוויות שנמצאו)
def estimate_potential_score(n):
    if n >= 9:
        return "🟢🟢 95–100%"
    elif n == 8:
        return "🟢 90–95%"
    elif n >= 7:
        return "🟢 85–89%"
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

# =========================
#  שליחה בטוחה ל-HTML
# =========================
def _split_html_safe(text: str, max_bytes: int = 3900):
    """מפצל טקסט לקטעים בטוחים ל-HTML:
    לא שובר תגיות <b>/<i>/<u>/<code>, סוגר אותן בסוף חלק ופותח מחדש בחלק הבא.
    """
    parts = []
    open_tags = []   # נעקוב אחרי סדר פתיחת תגיות
    buf = ''

    def update_stack(stack, seg):
        for m in re.finditer(r'<(/?)(b|i|u|code)>', seg):
            closing, tag = m.group(1) == '/', m.group(2)
            if closing:
                if tag in stack:
                    idx = len(stack) - 1 - stack[::-1].index(tag)
                    stack = stack[:idx] + stack[idx+1:]
            else:
                stack.append(tag)
        return stack

    for line in text.splitlines(True):  # שומר \n
        candidate = buf + line
        if len(candidate.encode('utf-8')) <= max_bytes:
            buf = candidate
        else:
            # סגור תגיות פתוחות בסוף החלק
            closed = buf + ''.join(f'</{t}>' for t in reversed(open_tags))
            parts.append(closed)
            # פתח שוב בתחילת החלק הבא
            buf = ''.join(f'<{t}>' for t in open_tags) + line
        open_tags = update_stack(open_tags, line)

    if buf:
        closed = buf + ''.join(f'</{t}>' for t in reversed(open_tags))
        parts.append(closed)
    return parts

def send_telegram_message(message: str):
    """שולח הודעה מפוצלת בבטחה כ-HTML, ללא שבירת תגיות וללא חריגה מהמגבלת בתים."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסר TELEGRAM_TOKEN או CHAT_ID")
        return
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        for part in _split_html_safe(message, max_bytes=3900):
            bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=part,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"שגיאת טלגרם: {e}")

# =========================
#  תוספת: 30 יום קדימה — 95%-100% ו-90%-95%
# =========================
def _count_money_aspects_for_datetime(birth_chart, fortune_birth, date_str, time_str, orb_deg=3):
    """סופר זוויות בין MONEY_OBJECTS (לידה) לבין MONEY_OBJECTS (טרנזיט) בזמן נתון."""
    transit_chart = create_chart(date_str, time_str)
    fortune_now = calculate_part_of_fortune(transit_chart)

    count = 0
    for p1 in MONEY_OBJECTS:
        pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
        for p2 in MONEY_OBJECTS:
            pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
            ang_val = calc_angle(pos1, pos2)
            for h_angle in HARMONIC_ANGLES:
                if abs(ang_val - h_angle) <= orb_deg:
                    count += 1
    return count

def _dedupe_times_keep_max(times_with_counts, merge_minutes=60):
    """מאחד זמנים סמוכים (≤ merge_minutes) ושומר את הגבוה."""
    if not times_with_counts:
        return []
    times_with_counts.sort(key=lambda x: x[0])
    merged = [times_with_counts[0]]
    for dt, cnt in times_with_counts[1:]:
        last_dt, last_cnt = merged[-1]
        if abs((dt - last_dt).total_seconds()) <= merge_minutes * 60:
            if cnt > last_cnt:
                merged[-1] = (dt, cnt)
        else:
            merged.append((dt, cnt))
    return merged

def find_30d_windows_90_95_and_95_100(step_minutes=30, dedupe_minutes=60):
    """
    סורק 30 יום קדימה (ברזולוציית חצי שעה) ומחזיר שתי רשימות:
    - hits95: כל הזמנים עם n_aspects >= 9  → 95%-100%
    - hits90: כל הזמנים עם n_aspects == 8  → 90%-95%
    """
    tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(tz).replace(second=0, microsecond=0)
    end = now + timedelta(days=30)

    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)

    hits95 = []
    hits90 = []
    t = now
    while t <= end:
        date_str = t.strftime('%Y/%m/%d')
        time_str = t.strftime('%H:%M')
        n_aspects = _count_money_aspects_for_datetime(
            birth_chart, fortune_birth, date_str, time_str, orb_deg=3
        )
        if n_aspects >= 9:
            hits95.append((t, n_aspects))
        elif n_aspects == 8:
            hits90.append((t, n_aspects))
        t += timedelta(minutes=step_minutes)

    hits95 = _dedupe_times_keep_max(hits95, merge_minutes=dedupe_minutes)
    hits90 = _dedupe_times_keep_max(hits90, merge_minutes=dedupe_minutes)

    hits95.sort(key=lambda x: x[1], reverse=True)
    hits90.sort(key=lambda x: x[1], reverse=True)
    return hits90, hits95

def build_30d_tail_90_95_and_95_100():
    """בונה בלוק טקסט לסוף ההודעה עם כל הזמנים 90%-95% ו-95%-100% ב-30 יום קדימה."""
    hits90, hits95 = find_30d_windows_90_95_and_95_100(step_minutes=30, dedupe_minutes=60)

    if not hits90 and not hits95:
        return "\n\n🍀 30 יום קדימה — אין חלונות 90%-100%."

    parts = ["\n\n🍀 30 יום קדימה — חלונות חזקים:\n"]

    if hits95:
        parts.append("✅ 95%-100%:\n" + "\n".join(
            f"• {dt.strftime('%d/%m/%Y %H:%M')} — 95%-100%" for dt, _ in hits95
        ))
    else:
        parts.append("✅ 95%-100%: (אין)\n")

    if hits90:
        parts.append("\n⬆️ 90%-95%:\n" + "\n".join(
            f"• {dt.strftime('%d/%m/%Y %H:%M')} — 90%-95%" for dt, _ in hits90
        ))
    else:
        parts.append("\n⬆️ 90%-95%: (אין)")

    return "\n".join(parts)

# =========================
#  בנייה ושליחה: 3 ימים + זנב 30 יום (90%-95% ו-95%-100%)
# =========================
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
        retro_now = [p for p in PLANETS if transit_chart_noon.get(p).isRetrograde()]
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
        message += f"🟢 <i>המלצה: למלא לוטו, חישגד או צ'אנס סביב {best}</i>\n\n"

    # הוספת זנב של 30 יום — גם 95%-100% וגם 90%-95%
    message += build_30d_tail_90_95_and_95_100()

    send_telegram_message(message)

# === הפעלה
if __name__ == '__main__':
    build_and_send_forecast()
