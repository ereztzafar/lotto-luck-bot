import os
import re
from collections import defaultdict
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

# === אובייקטים אסטרולוגיים ===
PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]
ALL_OBJECTS = PLANETS + ['FORTUNE']
MONEY_OBJECTS = [const.VENUS, const.JUPITER, const.MOON, const.PLUTO, const.URANUS, 'FORTUNE']

# נבדוק את כל הזוויות, אבל הניקוד משוקלל; לאוראנוס נספור רק 120°.
HARMONIC_ANGLES = [0, 60, 120, 180]

# === טווח שעות לתחזית 3 ימים ===
START_HOUR = 1
END_HOUR = 24
INTERVAL = 3

# === תצורת ניקוד/דיוק ===
BASE_ORB = 3                 # אורביס קבוע (°)
DEDUPE_MINUTES = 120         # איחוד חלונות סמוכים ברשימת 30 יום
STEP_MINUTES = 15            # דגימה ראשונית 30 יום
REFINE_WINDOW = 30           # ליטוש פיק ±דקות
REFINE_STEP = 2              # צעד ליטוש (דקות)
MAX_URANUS_PER_MIN = 2       # כמה תרומות אורנוס מותר בדקה

# ספים לניקוד משוקלל (לא "מספר היבטים"):
SCORE_95 = 14.0              # ≥ → 95%-100%
SCORE_90 = 11.5              # [11.5,14) → 90%-95%

BENEFICS = {const.VENUS, const.JUPITER, 'FORTUNE'}  # מיטיבים/PoF

# === סמלים ===
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

# === עזרי אסטרולוגיה ===
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

def _orb_for_pair(p1, p2, base=BASE_ORB):
    return base  # פשוט וקבוע: 3°

# משקל היבט (float) לפי זווית וזהות הכוכבים
def aspect_weight(p1, p2, h_angle):
    involves_uranus = (p1 == const.URANUS or p2 == const.URANUS)
    benefic_involved = (p1 in BENEFICS or p2 in BENEFICS)

    # אוראנוס: רק 120° נספר, עם משקל גבוה; 0/60/180 לא נספרים (180° רק אזהרה)
    if involves_uranus:
        if h_angle == 120:
            return 2.0
        else:
            return 0.0

    # ללא אוראנוס — משקל לפי זווית והאם יש מיטיב/PoF
    if h_angle == 120:
        return 2.0 if benefic_involved else 1.5
    if h_angle == 60:
        return 1.0 if benefic_involved else 0.5
    if h_angle in (0, 180):
        return 0.5 if benefic_involved else 0.0
    return 0.0

# מדרג מילולי על בסיס ניקוד משוקלל
def estimate_potential_score(score):
    if score >= SCORE_95:
        return "🟢🟢 95–100%"
    elif score >= SCORE_90:
        return "🟢 90–95%"
    elif score >= 7.5:
        return "🟢 85–89%"
    elif score >= 5.0:
        return "🟢 70–84%"
    elif score >= 3.0:
        return "🟡 50–69%"
    elif score > 0:
        return "🔘 30–49%"
    else:
        return "⬜ 0%"

# =========================
#  שליחה בטוחה ל-HTML
# =========================
def _split_html_safe(text: str, max_bytes: int = 3900):
    parts, open_tags, buf = [], [], ''
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
    for line in text.splitlines(True):
        candidate = buf + line
        if len(candidate.encode('utf-8')) <= max_bytes:
            buf = candidate
        else:
            parts.append(buf + ''.join(f'</{t}>' for t in reversed(open_tags)))
            buf = ''.join(f'<{t}>' for t in open_tags) + line
        open_tags = update_stack(open_tags, line)
    if buf:
        parts.append(buf + ''.join(f'</{t}>' for t in reversed(open_tags)))
    return parts

def send_telegram_message(message: str):
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
#  תחזית 3 ימים — ניקוד משוקלל + אזהרות אוראנוס 180°
# =========================
def find_lucky_hours(date_obj, birth_chart, fortune_birth):
    date_str = date_obj.strftime('%Y/%m/%d')
    lucky_blocks = []

    for hour in range(START_HOUR, END_HOUR + 1, INTERVAL):
        time_str = f"{hour:02d}:00"
        transit_chart = create_chart(date_str, time_str)
        fortune_now = calculate_part_of_fortune(transit_chart)

        found_aspects, warnings = [], []
        score_sum = 0.0
        uranus_used = 0

        for p1 in MONEY_OBJECTS:
            pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
            for p2 in MONEY_OBJECTS:
                pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
                ang_val = calc_angle(pos1, pos2)
                for h_angle in HARMONIC_ANGLES:
                    if abs(ang_val - h_angle) <= _orb_for_pair(p1, p2):
                        icon1 = PLANET_ICONS.get(p1, p1)
                        icon2 = PLANET_ICONS.get(p2, p2)
                        meaning = ANGLE_MEANINGS.get(h_angle, "")
                        label = f"{icon1} {p1} ↔ {icon2} {p2} — {h_angle}° {meaning}"

                        involves_uranus = (p1 == const.URANUS or p2 == const.URANUS)
                        if involves_uranus and h_angle == 180:
                            warnings.append("⚠️ אוראנוס באופוזיציה (180°) — תנודתיות")
                            found_aspects.append("⚠️ " + label)
                            continue

                        w = aspect_weight(p1, p2, h_angle)
                        if w > 0:
                            if involves_uranus:
                                if uranus_used < MAX_URANUS_PER_MIN:
                                    score_sum += w
                                    uranus_used += 1
                            else:
                                score_sum += w
                        found_aspects.append(label)

        if found_aspects:
            lucky_blocks.append({
                'שעה': time_str,
                'זוויות': found_aspects,
                'score_sum': round(score_sum, 2),
                'warnings': warnings
            })
    return lucky_blocks

# =========================
#  30 יום קדימה — ניקוד משוקלל + "חתימת זהב"
# =========================
def _score_for_datetime(birth_chart, fortune_birth, date_str, time_str):
    """מחזיר (score_sum, has_key_trine)"""
    transit_chart = create_chart(date_str, time_str)
    fortune_now = calculate_part_of_fortune(transit_chart)

    score_sum = 0.0
    uranus_used = 0
    has_key_trine = False  # טריין 120° אל צדק/ונוס/PoF

    for p1 in MONEY_OBJECTS:
        pos1 = birth_chart.get(p1).lon if p1 != 'FORTUNE' else fortune_birth
        for p2 in MONEY_OBJECTS:
            pos2 = transit_chart.get(p2).lon if p2 != 'FORTUNE' else fortune_now
            ang_val = calc_angle(pos1, pos2)
            for h_angle in HARMONIC_ANGLES:
                if abs(ang_val - h_angle) <= _orb_for_pair(p1, p2):
                    involves_uranus = (p1 == const.URANUS or p2 == const.URANUS)
                    if involves_uranus and h_angle == 180:
                        continue

                    # חתימת זהב: 120° למיטיב/PoF
                    if h_angle == 120 and (p1 in BENEFICS or p2 in BENEFICS):
                        has_key_trine = True

                    w = aspect_weight(p1, p2, h_angle)
                    if w > 0:
                        if involves_uranus:
                            if uranus_used < MAX_URANUS_PER_MIN:
                                score_sum += w
                                uranus_used += 1
                        else:
                            score_sum += w
    return score_sum, has_key_trine

def _dedupe_times_keep_max(times_with_scores, merge_minutes=DEDUPE_MINUTES):
    if not times_with_scores:
        return []
    times_with_scores.sort(key=lambda x: x[0])
    merged = [times_with_scores[0]]
    for dt, sc in times_with_scores[1:]:
        last_dt, last_sc = merged[-1]
        if abs((dt - last_dt).total_seconds()) <= merge_minutes * 60:
            if sc > last_sc:
                merged[-1] = (dt, sc)
        else:
            merged.append((dt, sc))
    return merged

def _refine_peak_around(t, birth_chart, fortune_birth, window=REFINE_WINDOW, step=REFINE_STEP):
    best_t = t
    best_s, best_key = _score_for_datetime(birth_chart, fortune_birth, t.strftime('%Y/%m/%d'), t.strftime('%H:%M'))
    for delta in range(-window, window + 1, step):
        if delta == 0:
            continue
        tt = t + timedelta(minutes=delta)
        s, key = _score_for_datetime(birth_chart, fortune_birth, tt.strftime('%Y/%m/%d'), tt.strftime('%H:%M'))
        if s > best_s:
            best_s, best_t, best_key = s, tt, key
    return best_t, best_s, best_key

def _limit_per_day(hits, max_per_day=2):
    """מגביל לכל היותר max_per_day חלונות ליום (הגבוהים ביותר)."""
    by_day = defaultdict(list)
    for dt, sc in hits:
        key = dt.strftime('%Y-%m-%d')
        by_day[key].append((dt, sc))
    trimmed = []
    for key, items in by_day.items():
        items.sort(key=lambda x: x[1], reverse=True)
        trimmed.extend(items[:max_per_day])
    trimmed.sort(key=lambda x: x[0])
    return trimmed

def find_30d_windows_weighted(step_minutes=STEP_MINUTES, dedupe_minutes=DEDUPE_MINUTES):
    tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(tz)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=30)

    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)

    hits95, hits90 = [], []
    t = start
    while t <= end:
        s, key = _score_for_datetime(birth_chart, fortune_birth, t.strftime('%Y/%m/%d'), t.strftime('%H:%M'))

        # ליטוש סביב נקודה רק אם קרובים לסף
        if s >= (SCORE_90 - 1.5):
            best_t, best_s, best_key = _refine_peak_around(t, birth_chart, fortune_birth)
        else:
            best_t, best_s, best_key = t, s, key

        # סינון: חייבת להיות "חתימת זהב" (120° אל צדק/ונוס/PoF)
        if not best_key:
            t += timedelta(minutes=step_minutes)
            continue

        if best_s >= SCORE_95:
            hits95.append((best_t, best_s))
        elif best_s >= SCORE_90:
            hits90.append((best_t, best_s))

        t += timedelta(minutes=step_minutes)

    # איחוד סמוכים + הגבלת 2 חלונות ליום לכל קטגוריה
    hits95 = _dedupe_times_keep_max(hits95, merge_minutes=dedupe_minutes)
    hits90 = _dedupe_times_keep_max(hits90, merge_minutes=dedupe_minutes)
    hits95 = _limit_per_day(hits95, max_per_day=2)
    hits90 = _limit_per_day(hits90, max_per_day=2)
    return hits90, hits95

def build_30d_tail_weighted():
    hits90, hits95 = find_30d_windows_weighted()

    if not hits90 and not hits95:
        return "\n\n🍀 30 יום קדימה — אין חלונות 90%-100%."

    parts = ["\n\n🍀 30 יום קדימה — חלונות חזקים (ניקוד משוקלל):\n"]
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
#  בנייה ושליחה
# =========================
def build_and_send_forecast():
    tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(tz)
    birth_chart = create_chart(BIRTH_DATE, BIRTH_TIME)
    fortune_birth = calculate_part_of_fortune(birth_chart)

    message = f"📆 <b>תחזית לוטו אסטרולוגית – 3 הימים הקרובים 🎟️</b>\n"
    message += f"🧬 לפי מפת לידה: {BIRTH_DATE} {BIRTH_TIME} פ\"ת\n"
    message += f"🎯 ניקוד משוקלל (120° מועדף; אוראנוס נספר רק ב־120°, 180°=אזהרה):\n\n"

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
            score = block.get('score_sum', 0.0)
            percent = estimate_potential_score(score)
            message += f"🕐 <b>{block['שעה']}</b> – 💰 פוטנציאל זכייה: {percent} (ניקוד {score})\n"
            for asp in block['זוויות']:
                message += f"• {asp}\n"
            for w in block.get('warnings', []):
                message += f"{w}\n"
            message += "\n"

        best = max(lucky_hours, key=lambda x: x.get('score_sum', 0.0))['שעה']
        message += f"🟢 <i>המלצה: למלא לוטו, חישגד או צ'אנס סביב {best}</i>\n\n"

    message += build_30d_tail_weighted()
    send_telegram_message(message)

# === הפעלה
if __name__ == '__main__':
    build_and_send_forecast()
