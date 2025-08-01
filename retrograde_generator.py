import json
from datetime import date, timedelta
import ephem
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.datetime import Date
from flatlib import const

PLANET_TRANSLATIONS = {
    const.MERCURY: "מרקורי",
    const.VENUS: "ונוס",
    const.MARS: "מאדים",
    const.JUPITER: "צדק",
    const.SATURN: "שבתאי",
    const.URANUS: "אוראנוס",
    const.NEPTUNE: "נפטון",
    const.PLUTO: "פלוטו"
}

EXPLANATIONS = {
    "מרקורי": "מומלץ להימנע מחתימה על חוזים או תקשורת חשובה.",
    "ונוס": "נסיגה שמדגישה עיכובים בקשרים רומנטיים וכספיים.",
    "מאדים": "כדאי להיזהר מפעולות פזיזות או קונפליקטים.",
    "צדק": "זהירות מהגזמות או הבטחות שווא.",
    "שבתאי": "מומלץ להימנע מהחלטות כלכליות גדולות בזמן נסיגת שבתאי.",
    "אוראנוס": "נסיגה זו עשויה להביא שינויים בלתי צפויים פנימה.",
    "נפטון": "היזהרו מערפול, בלבול או אשליות.",
    "פלוטו": "נסיגת פלוטו מצביעה על תהליכים פנימיים עמוקים שדורשים עיבוד."
}

def create_chart(date_str, time_str, location):
    dt = Date(date_str, time_str)
    dt_ephem = ephem.Date(f"{date_str} {time_str}:00")  # סוג תאריך תואם ephem
    return Chart(ephem.Date(f"{date_str} {time_str}:00"), location), ephem.Date(f"{date_str} {time_str}:00")



def generate_retrogrades(start_date, end_date):
    location = GeoPos("32n5", "34e53")
    planets = list(PLANET_TRANSLATIONS.keys())
    result = {}

    for day in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y/%m/%d")
        key = current_date.strftime("%Y-%m-%d")
        chart, dt_ephem = create_chart(date_str, "12:00", location)


        retro_list = []
        for planet in planets:
            try:
                obj = chart.get(planet)
                if hasattr(obj, 'isRetro') and obj.isRetro():
                    heb_name = PLANET_TRANSLATIONS[planet]
                    retro_list.append({
                        "planet": heb_name,
                        "explanation": EXPLANATIONS[heb_name]
                    })
            except KeyError:
                print(f"⚠️ כוכב {planet} לא נמצא במפה")

        if retro_list:
            result[key] = retro_list

    with open("retrogrades.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ קובץ retrogrades.json עודכן עבור {len(result)} ימים")

if __name__ == "__main__":
    today = date.today()
    future = today + timedelta(days=30)
    generate_retrogrades(today, future)
