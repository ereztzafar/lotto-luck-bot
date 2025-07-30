from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const

import swisseph as swe

# פרטי הלידה שלך
birth_date = '1970/11/22'
birth_time = '06:00'
location = GeoPos('32n05', '34e53')  # פתח תקווה

# Step 1: צור מפת לידה רגילה
birth_dt = Datetime(birth_date, birth_time, '+02:00')
chart = Chart(birth_dt, location, IDs=const.LIST_OBJECTS)

# Step 2: חישוב מיקום Lilith ו־Chiron באמצעות Swiss Ephemeris
def get_body_position(body_id, date_str):
    year, month, day = map(int, date_str.split('-'))
    jd = swe.julday(year, month, day)
    lon, lat, dist = swe.calc_ut(jd, body_id)
    return lon

# Step 3: הוספת כוכבים ידניים (Lilith ו־Chiron) למפה
LILITH_ID = swe.SE_MEAN_APOG
CHIRON_ID = swe.SE_CHIRON

lilith_lon = get_body_position(LILITH_ID, birth_date)
chiron_lon = get_body_position(CHIRON_ID, birth_date)

print(f"🌑 Lilith (Mean Apogee): {lilith_lon:.2f}°")
print(f"🧬 Chiron: {chiron_lon:.2f}°")

# אם תרצה, אפשר לשלב אותם גם לתוך גרף או ל־chart.objects
# כרגע זה הדפסה בלבד

# הדפסת כוכבים רגילים מהמפה
print("\n🌌 מפת לידה רגילה:")
for obj in const.LIST_OBJECTS:
    print(f"{obj}: {chart.get(obj)}")
