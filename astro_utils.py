from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.datetime import Datetime

def create_chart(date_str, time_str, location_str):
    """
    Create an astrology chart from date, time, and location.
    """
    date = date_str
    time = time_str
    pos = GeoPos(*location_str.split(','))
    return Chart(Datetime(date, time, '+02:00'), pos)
