import datetime
import json
from flatlib import const
from flatlib.geopos import GeoPos
from astro_utils import create_chart

RETRO_FILE = "retrogrades.json"

def get_retrogrades(chart):
    retrogrades = []

    planets = {
        const.MERCURY: "מרקורי – זהירות בנסיעות, תקשורת, טעויות",
        const.VENUS: "ונוס – קושי בזוגיות או כספים",
        const.MARS: "מאדים – אנרגיה נמוכה, עימותים פנימיים",
        const.JUPITER: "צדק – עיכוב בהצלחה, צורך בלמידה פנימית",
        const.SATURN: "שבתאי – מומלץ להימנע מהחלטות כלכליות גדולות בזמן נסיגת שבתאי.",
        const.URANUS: "אורנוס – שינויים בלתי צפויים בולמים",
        const.NEPTUNE: "נפטון – טשטוש, אשליה, צריך לשמור על בהירות",
        const.PLUTO: "פלוטו – תהליכים פנימיים עמוקים שדורשים עיבוד",
        const.CHIRON: "כירון – ריפוי פצעים ישנים",
        const.LILITH: "לילית – תחושת חוסר שקט או צללים רגשיים"
    }

    for name, explanation in planets.items():
        try:
            obj = chart.get(name)
            if obj.retro:
                retrogrades.append({
                    "planet": obj.id,
                    "explanation": explanation
                })
        except:
            continue

    return retrogrades

def main():
    today = datetime.datetime.now()
    date_str = today.strftime('%Y/%m/%d')
    date_key = today.strftime('%Y-%m-%d')
    time_str = "12:00"

    pos = GeoPos("32n5", "34e53")  # פתח תקווה
    chart = create_chart(date_str, time_str, pos)

    retrogrades = get_retrogrades(chart)

    if not retrogrades:
        print("❌ אין כוכבים בנסיגה")
        return

    # טעינת קובץ קיים אם יש
    if os.path.exists(RETRO_FILE):
        with open(RETRO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # עדכון התאריך הנוכחי
    data[date_key] = retrogrades

    # שמירה
    with open(RETRO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ נשמרו {len(retrogrades)} נסיגות ל־{date_key}")

if __name__ == "__main__":
    main()
