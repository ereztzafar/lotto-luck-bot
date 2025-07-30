from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const

# נתוני לידה: תאריך, שעה, מיקום
birth_dt = Datetime('1970/11/22', '06:00', '+02:00')
birth_pos = GeoPos('32.0871', '34.8869')  # פתח תקווה

# רק גרמי שמיים רגילים: שמש, ירח, מרקורי, ונוס, מארס, צדק, שבתאי, אוראנוס, נפטון, פלוטו
objects = const.LIST_OBJECTS  # אין לילית, אין אפוגיאה

# צור את מפת הלידה
chart = Chart(birth_dt, birth_pos, IDs=objects)

# הדפס את מיקום כל גרם שמיים
for obj in chart.objects:
    print(f'{obj.id}: {obj.sign} {obj.lon}')
