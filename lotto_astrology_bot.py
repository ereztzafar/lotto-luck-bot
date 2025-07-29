from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, ephem
import os
import requests
from datetime import datetime

# פרטי לידה – פתח תקווה
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')

# קביעת אזור זמן לפי תאריך (שעון חורף/קיץ)
def get_timezone():
    today = datetime.utcnow()
    year = today.year
    summer_start = datetime(year, 3, 28)
    winter_start = datetime(year, 10, 30)
    return '+03:00' if summer_start <= today < winter_start else '+02:00'

# טעינת סודות מה־GitHub Secrets
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID ב־Secrets")
    return token, chat_id

# שליחת הודעה
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code}")

# תחזית אסטרולוגית מלאה
def get_astrology_forecast():
    tz = get_timezone()
    now = datetime.utcnow().strftime('%Y/%m/%d %H:%M')
    dt = Datetime(now.split()[0], now.split()[1], tz)

    try:
        chart = Chart(dt, BIRTH_PLACE, IDs=ephem.LIST_OBJECTS)
    except Exception as e:
        return f"❌ שגיאה ביצירת מפת לידה: {e}"

    objects = {
        "☀️ שמש": const.SUN,
        "🌙 ירח": const.MOON,
        "☿ מרקורי": const.MERCURY,
        "♀ ונוס": const.VENUS,
        "♂ מארס": const.MARS,
        "♃ צדק": const.JUPITER,
        "♄ שבתאי": const.SATURN,
        "♅ אורנוס": const.URANUS,
        "♆ נפטון": const.NEPTUNE,
        "♇ פלוטו": const.PLUTO,
    }

    forecast = f"🔮 תחזית אסטרולוגית ל־{dt.time} (UTC{tz}):\n\n"
    signs = {}

    for name, obj in objects.items():
        planet = chart.get(obj)
        deg = int(planet.lon)
        min = int((planet.lon - deg) * 60)
        forecast += f"{name} במזל {planet.sign} {deg}°{min:02d}′\n"
        signs[obj] = planet.sign

    # ניתוח חכם לסיכויי זכייה
    score = 0

    if signs[const.JUPITER] in ['Taurus', 'Pisces', 'Cancer']:
        score += 2
    if signs[const.VENUS] in ['Leo', 'Libra']:
        score += 1
    if signs[const.MOON] in ['Scorpio', 'Capricorn']:
        score -= 1
    if signs[const.SATURN] in ['Aquarius', 'Capricorn']:
        score -= 1
    if signs[const.SUN] in ['Sagittarius']:
        score += 1
    if signs[const.MERCURY] in ['Gemini', 'Virgo']:
        score += 1
    if signs[const.URANUS] == 'Aries':
        score += 1
    if signs[const.PLUTO] in ['Scorpio']:
        score += 1
    if signs[const.NEPTUNE] in ['Pisces']:
        score += 1

    # קביעת רמת מזל
    if score >= 4:
        level = "🟢 סיכוי גבוה לזכייה היום!"
    elif 1 <= score < 4:
        level = "🟡 סיכוי בינוני – שווה לנסות חישגד או צ'אנס."
    else:
        level = "🔴 לא מומלץ היום – שמור את הכסף למחר."

    forecast += f"\n🎲 {level}"

    return forecast.strip()

# הפעלה
if __name__ == "__main__":
    message = get_astrology_forecast()
    send_telegram_message(message)
