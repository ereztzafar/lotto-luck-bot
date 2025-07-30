from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import ephem
import swisseph as swe
import json
import datetime

# פרטי לידה – פתח תקווה
birth_date = '1970/11/22'
birth_time = '06:00'
timezone = '+02:00'
birth_pos = GeoPos('32n05', '34e53')
birth_dt = Datetime(birth_date, birth_time, timezone)

# כוכבים רגילים + לילית (אבל בלי כירון עדיין)
objects = ephem.MAJOR_OBJECTS + ['LILITH']
chart = Chart(birth_dt, birth_pos, IDs=objects)

# תוצאה סופית
birth_data = {}

# 1. כוכבים רגילים
for obj in objects:
    planet = chart.get(obj)
    deg = int(planet.lon)
    minute = int((planet.lon - deg) * 60)
    birth_data[obj] = {
        'sign': planet.sign,
        'lon_deg': deg,
        'lon_min': minute
    }

# 2. כירון דרך pyswisseph
birth_datetime = datetime.datetime.strptime(birth_date + ' ' + birth_time, "%Y/%m/%d %H:%M")
jd_ut = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day,
                   birth_datetime.hour + birth_datetime.minute / 60.0)

lat = float(birth_pos.lat.replace('n', '').replace('s', '-'))
lon = float(birth_pos.lon.replace('e', '').replace('w', '-'))
swe.set_topo(lon, lat, 0)

chiron = swe.calc_ut(jd_ut, swe.CHIRON)[0]
chiron_lon = chiron[0]
deg = int(chiron_lon)
minute = int((chiron_lon - deg) * 60)
signs = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
sign_index = deg // 30
sign = signs[sign_index]

birth_data['CHIRON'] = {
    'sign': sign,
    'lon_deg': deg % 30,
    'lon_min': minute
}

# שמירה לקובץ
with open('birth_chart.json', 'w', encoding='utf-8') as f:
    json.dump(birth_data, f, ensure_ascii=False, indent=2)

print("✅ מפת הלידה נשמרה בהצלחה (כולל כירון)")
