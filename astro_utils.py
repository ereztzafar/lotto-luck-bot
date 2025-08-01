from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

def create_chart(date_str, time_str, location):
    if isinstance(location, str):
        lat, lon = location.split(',')
        pos = GeoPos(lat, lon)
    else:
        pos = location  # כבר אובייקט מסוג GeoPos

    dt = Datetime(date_str, time_str, '+02:00')
    return Chart(dt, pos, useSwissEphem=True)  # ⚠️ קריטי בשביל obj.retro

