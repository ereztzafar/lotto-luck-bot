from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from datetime import datetime, timedelta

BIRTH_PLACE = GeoPos('32n05', '34e53')  # פתח תקווה

def get_lucky_hours(date_str, tz):
    lucky_planets = [const.JUPITER, const.VENUS, const.SUN]
    result = []

    base_time = datetime.strptime(date_str + " 05:00", '%Y/%m/%d %H:%M')
    for i in range(0, 18):  # כל שעה בין 05:00 ל־22:00
        dt = base_time + timedelta(hours=i)
        flat_dt = Datetime(dt.strftime('%Y/%m/%d'), dt.strftime('%H:%M'), tz)
        chart = Chart(flat_dt, BIRTH_PLACE)

        asc = chart.get(const.ASC)
        ruler = chart.get(asc.ruler)

        if ruler.id in lucky_planets:
            result.append(dt.strftime('%H:%M'))

    return result
