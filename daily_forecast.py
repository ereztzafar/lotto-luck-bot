from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

def generate_forecast(date, time, location_str):
    pos = GeoPos(*location_str.split(','))
    chart = Chart(Datetime(date, time, '+02:00'), pos)
    aspects = chart.getAspects()
    forecast = []
    for asp in aspects:
        forecast.append(f"{asp.obj1} {asp.type} {asp.obj2}")
    return forecast
