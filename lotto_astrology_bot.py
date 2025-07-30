from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, aspects
import os
import requests
from datetime import datetime, timedelta
from pytz import timezone

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')

# טבלת שליטים קלאסיים של המזלות
RULERS = {
    'Aries': const.MARS,
    'Taurus': const.VENUS,
    'Gemini': const.MERCURY,
    'Cancer': const.MOON,
    'Leo': const.SUN,
    'Virgo': const.MERCURY,
    'Libra': const.VENUS,
    'Scorpio': const.MARS,
    'Sagittarius': const.JUPITER,
    'Capricorn': const.SATURN,
    'Aquarius': const.SATURN,
    'Pisces': const.JUPITER,
}

# קביעת אזור זמן לפי תאריך (שעון חורף/קיץ)
def get_timezone():
    today = datetime.utcnow()
    year = today.year
    summer_start = datetime(year, 3, 29)
    winter_start = datetime(year, 10, 27)
    return '+03:00' if summer_start <= today < winter_start else '+02:00'

# משתני סביבה (GitHub Actions)
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID")
    return token, chat_id

# שליחת הודעה בטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code}")

# חישוב שעות מזל אישיות
def get_lucky_hours(date_str, tz):
    lucky_planets = [const.JUPITER, const.VENUS, const.SUN]
    result = []
    base_time = datetime.strptime(date_str + " 05:00", '%Y/%m/%d %H:%M')
    for i in range(0, 18):  # מ-05:00 עד 22:00
        dt = base_time + timedelta(hours=i)
        flat_dt = Datetime(dt.strftime('%Y/%m/%d'), dt.strftime('%H:%M'), tz)
        chart = Chart(flat_dt, BIRTH_PLACE)
        asc = chart.get(const.ASC)
        asc_sign = asc.sign
        ruler_id = RULERS.get(asc_sign)  # ← שליט האופק מתוך טבלת RULERS
        if ruler_id in lucky_planets:
            result.append(dt.strftime('%H:%M'))
    return result

# השוואת מפת טרנזיט למפת לידה
# השוואת מפת טרנזיט למפת לידה
def compare_transit_to_birth(transit_chart, birth_chart):
    relevant = [
        const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
        const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
    ]
    
    # הגדרת זוויות עיקריות (מאחר ואין ב-flatlib משתנה קבוע כזה)
    MAJOR_ASPECTS = ['CONJUNCTION', 'SEXTILE', 'SQUARE', 'TRINE', 'OPPOSITION']
    
    results = []
    for t_obj in relevant:
        for b_obj in relevant:
            angle = aspects.getAspect(transit_chart.get(t_obj), birth_chart.get(b_obj), MAJOR_ASPECTS)
            if angle:
                aspect_name = angle[0]
                orb = angle[1]
                if abs(orb) <= 3:
                    results.append(f"{t_obj} {aspect_name} ל־{b_obj} (אורב {orb:.1f}°)")
    return results



# התחזית האסטרולוגית + שעות מזל
def get_astrology_forecast():
    tz = get_timezone()
    now = datetime.utcnow()
    local_now = datetime.now(timezone('Asia/Jerusalem')).strftime('%H:%M')
    today_str = now.strftime('%Y/%m/%d')
    dt = Datetime(today_str, now.strftime('%H:%M'), tz)

    objects = [
        const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
        const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
    ]

    names = {
        const.SUN: "☀️ שמש", const.MOON: "🌙 ירח", const.MERCURY: "☿ מרקורי",
        const.VENUS: "♀ ונוס", const.MARS: "♂ מארס", const.JUPITER: "♃ צדק",
        const.SATURN: "♄ שבתאי", const.URANUS: "♅ אורנוס", const.NEPTUNE: "♆ נפטון", const.PLUTO: "♇ פלוטו",
    }

    try:
        transit_chart = Chart(dt, BIRTH_PLACE, IDs=objects)
        birth_dt = Datetime(BIRTH_DATE, BIRTH_TIME, tz)
        birth_chart = Chart(birth_dt, BIRTH_PLACE, IDs=objects)
    except Exception as e:
        return f"❌ שגיאה ביצירת מפות: {e}"

    forecast = f"🔭 תחזית ל־{local_now} (שעון ישראל):\n\n"
    signs = {}
    score = 0
    reasons = []

    for obj in objects:
        planet = transit_chart.get(obj)
        deg = int(planet.lon)
        min = int((planet.lon - deg) * 60)
        retro = " ℞" if hasattr(planet, 'retro') and planet.retro else ""
        forecast += f"{names[obj]} במזל {planet.sign} {deg}°{min:02d}′{retro}\n"
        signs[obj] = planet.sign

        if hasattr(planet, 'retro') and planet.retro and obj in [const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]:
            score -= 1
            reasons.append(f"{names[obj]} בנסיגה – עלול לעכב מזל והצלחה (-1)")

    if signs[const.JUPITER] in ['Taurus', 'Pisces', 'Cancer']:
        score += 2
        reasons.append(f"♃ צדק במזל {signs[const.JUPITER]} – מזל טוב להצלחה וכסף (+2)")
    if signs[const.VENUS] in ['Leo', 'Libra']:
        score += 1
        reasons.append(f"♀ ונוס במזל {signs[const.VENUS]} – מגביר משיכה והרמוניה (+1)")
    if signs[const.MOON] in ['Scorpio', 'Capricorn']:
        score -= 1
        reasons.append(f"🌙 ירח במזל {signs[const.MOON]} – מגביר מתחים פנימיים (-1)")
    if signs[const.SATURN] in ['Aquarius', 'Capricorn']:
        score -= 1
        reasons.append(f"♄ שבתאי במזל {signs[const.SATURN]} – מגביל ומכביד על מזל אישי (-1)")
    if signs[const.SUN] == 'Sagittarius':
        score += 1
        reasons.append("☀️ שמש בקשת – מגביר אופטימיות והרפתקנות (+1)")
    if signs[const.MERCURY] in ['Gemini', 'Virgo']:
        score += 1
        reasons.append(f"☿ מרקורי במזל {signs[const.MERCURY]} – חדות שכלית ובחירה נכונה (+1)")
    if signs[const.URANUS] == 'Aries':
        score += 1
        reasons.append("♅ אורנוס בטלה – הפתעות נעימות ויצירתיות (+1)")
    if signs[const.PLUTO] == 'Scorpio':
        score += 1
        reasons.append("♇ פלוטו בעקרב – אומץ לקחת סיכונים אינטואיטיביים (+1)")
    if signs[const.NEPTUNE] == 'Pisces':
        score += 1
        reasons.append("♆ נפטון בדגים – תחושת הרמוניה וזרימה טובה להימורים (+1)")

    if score >= 4:
        level = "🟢 סיכוי גבוה לזכייה היום!"
    elif 1 <= score < 4:
        level = "🟡 סיכוי בינוני – שווה לנסות חישגד או צ'אנס."
    else:
        level = "🔴 לא מומלץ היום – שמור את הכסף למחר."

    lucky_hours = get_lucky_hours(today_str, tz)
    hours_str = ', '.join(lucky_hours) if lucky_hours else "אין שעות מזל היום."
    transit_aspects = compare_transit_to_birth(transit_chart, birth_chart)
    aspects_str = "\n".join(f"🔹 {a}" for a in transit_aspects) if transit_aspects else "לא נמצאו זוויות דומיננטיות."

    forecast += "\n\n🕰️ שעות מזל להיום:\n" + hours_str
    forecast += "\n\n📌 נימוקים לתחזית:\n" + '\n'.join(f"- {r}" for r in reasons)
    forecast += "\n\n🔁 זוויות בין כוכבי הטרנזיט למפת הלידה:\n" + aspects_str
    forecast += f"\n\n🎲 {level}"

    return forecast.strip()

# הרצה
if __name__ == "__main__":
    message = get_astrology_forecast()
    send_telegram_message(message)
