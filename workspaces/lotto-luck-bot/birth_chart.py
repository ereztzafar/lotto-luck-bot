from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const, ephem
import json

# פרטי לידה – פתח תקווה
birth_date = '1970/11/22'
birth_time = '06:00'
timezone = '+02:00'  # חורף
birth_pos = GeoPos('32n05', '34e53')
birth_dt = Datetime(birth_date, birth_time, timezone)

# יצירת מפת לידה
chart = Chart(birth_dt, birth_pos, IDs=ephem.MAJOR_OBJECTS)

# שמירת הכוכבים ומיקומם בקובץ JSON
birth_data = {}
for obj in ephem.MAJOR_OBJECTS:
    planet = chart.get(obj)
    deg = int(planet.lon)
    min = int((planet.lon - deg) * 60)
    birth_data[obj] = {
        'sign': planet.sign,
        'lon_deg': deg,
        'lon_min': min
    }

with open('birth_chart.json', 'w', encoding='utf-8') as f:
    json.dump(birth_data, f, ensure_ascii=False, indent=2)

print("✅ מפת הלידה נשמרה בהצלחה (birth_chart.json)")
