from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import json
import os
import requests

# פרטי לידה – פתח תקווה
birth_date = '1970/11/22'
birth_time = '06:00'
timezone = '+02:00'
birth_pos = GeoPos('32n05', '34e53')
birth_dt = Datetime(birth_date, birth_time, timezone)

# רשימת כוכבים ללא לילית וכירון
objects = [
    const.SUN,
    const.MOON,
    const.MERCURY,
    const.VENUS,
    const.MARS,
    const.JUPITER,
    const.SATURN,
    const.URANUS,
    const.NEPTUNE,
    const.PLUTO
]

# יצירת מפת לידה
chart = Chart(birth_dt, birth_pos, IDs=objects)

# שמירת מפת הלידה לקובץ JSON
birth_data = {}
for obj in objects:
    planet = chart.get(obj)
    deg = int(planet.lon)
    min = int((planet.lon - deg) * 60)
    birth_data[obj] = {
        'sign': planet.sign,
        'lon_deg': deg,
        'lon_min': min
    }

# שמירה לקובץ
file_path = 'birth_chart.json'
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(birth_data, f, ensure_ascii=False, indent=2)

print("✅ הקובץ birth_chart.json נוצר בהצלחה")

# שליחת הקובץ לטלגרם
def send_json_to_telegram(file_path, token, chat_id):
    with open(file_path, 'rb') as file:
        response = requests.post(
            f'https://api.telegram.org/bot{token}/sendDocument',
            data={'chat_id': chat_id},
            files={'document': file}
        )
    if response.status_code == 200:
        print("✅ הקובץ נשלח בהצלחה לטלגרם")
    else:
        print("❌ שגיאה בשליחה לטלגרם:", response.text)

# שליפה מה־ENV
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    send_json_to_telegram(file_path, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
else:
    print("⚠️ לא הוגדרו משתני סביבה TELEGRAM_TOKEN ו־TELEGRAM_CHAT_ID")
