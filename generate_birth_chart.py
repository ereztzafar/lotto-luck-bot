from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import os
import requests

# פרטי לידה – פתח תקווה
birth_date = '1970/11/22'
birth_time = '06:00'
timezone = '+02:00'
birth_pos = GeoPos('32n05', '34e53')
birth_dt = Datetime(birth_date, birth_time, timezone)

# כוכבים עיקריים בלבד
objects = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]

# יצירת מפת לידה
chart = Chart(birth_dt, birth_pos, IDs=objects)

# בניית טקסט יפה
lines = ["🌟 מפת לידה (22.11.1970 06:00 פתח תקווה):"]
for obj in objects:
    planet = chart.get(obj)
    deg = int(planet.lon)
    min = int((planet.lon - deg) * 60)
    lines.append(f"{obj:<8}: {deg}°{min:02}′ {planet.sign}")

msg = '\n'.join(lines)

# שליחת טקסט לטלגרם
def send_telegram_message(text, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ נשלח בהצלחה לטלגרם")
    else:
        print("❌ שגיאה בשליחה:", response.text)

# משתני סביבה
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    send_telegram_message(msg, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
else:
    print("⚠️ לא הוגדרו משתני סביבה TELEGRAM_TOKEN ו־TELEGRAM_CHAT_ID")
