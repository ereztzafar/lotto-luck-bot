from flatlib.chart import Chart
from flatlib import const
import math

def angle_diff(a, b):
    """הפרש בין זוויות בשעון (0–360)"""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)

def is_trine(a, b, orb=6):
    return abs(angle_diff(a, b) - 120) <= orb

def is_conjunction(a, b, orb=6):
    return angle_diff(a, b) <= orb

def is_square(a, b, orb=6):
    return abs(angle_diff(a, b) - 90) <= orb

def analyze_transits(birth_chart: Chart, transit_chart: Chart):
    score = 0
    highlights = []

    sun_transit = transit_chart.get(const.SUN)
    jupiter_birth = birth_chart.get(const.JUPITER)
    moon_transit = transit_chart.get(const.MOON)
    node_birth = birth_chart.get(const.NORTH_NODE)
    saturn_transit = transit_chart.get(const.SATURN)
    venus_birth = birth_chart.get(const.VENUS)

    if is_trine(sun_transit.lon, jupiter_birth.lon):
        score += 3
        highlights.append("☀️ השמש בטריין ליופיטר – מזל גדול")

    if is_conjunction(moon_transit.lon, node_birth.lon):
        score += 2
        highlights.append("🌕 ירח בצמידות לראש הדרקון – תחושת גורל")

    if is_square(saturn_transit.lon, venus_birth.lon):
        score -= 2
        highlights.append("⚠️ שבתאי בריבוע לונוס – עצירה זמנית")

    summary = "\n".join(highlights) if highlights else "אין השפעות משמעותיות כעת."

    # נורמליזציה לציון 0–10
    final_score = max(0, min(score + 5, 10))

    return {
        "score": final_score,
        "summary": summary
    }
