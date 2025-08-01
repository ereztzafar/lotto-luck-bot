from flatlib.geopos import GeoPos
from astro_utils import create_chart
from birth_chart_loader import load_birth_chart
from daily_forecast import find_lucky_hours
from telegram_sender import send_telegram_message, load_secrets
from flatlib import const
import datetime

def get_retrograde_planets(transit_chart):
    retrogrades = []
    planets = {
        const.MERCURY: "מרקורי – זהירות בנסיעות, תקשורת, טעויות",
        const.VENUS: "ונוס – קושי בזוגיות או כספים",
        const.MARS: "מאדים – אנרגיה נמוכה, עימותים פנימיים",
        const.JUPITER: "צדק – עיכוב בהצלחה, צורך בלמידה פנימית",
        const.SATURN: "שבתאי – שיעורים בקארמה, אתגרים בזמנים",
        const.URANUS: "אורנוס – שינויים לא צפויים מתעכבים",
        const.NEPTUNE: "נפטון – בלבול, דמיון מופרז, צורך בבהירות",
        const.PLUTO: "פלוטו – התמרה עמוקה, שחרור שליטה"
    }
    for p, explanation in planets.items():
        planet = transit_chart.get(p)
        if planet.isRetrograde:
            retrogrades.append((planet.id, explanation))
    return retrogrades

def main():
    # פרטי הלידה שלך
    birth_date = '1970/11/22'
    birth_time = '06:00'
    birth_location = GeoPos("32n5", "34e53")

    # יצירת מפת לידה
    birth_chart = create_chart(birth_date, birth_time, birth_location)

    # מפת טרנזיט נוכחית
    now = datetime.datetime.now()
    now_date = now.strftime('%Y/%m/%d')
    now_time = now.strftime('%H:%M')
    transit_chart = create_chart(now_date, now_time, birth_location)

    # שעות מזל
    lucky_hours = find_lucky_hours(birth_chart, transit_chart)  # ✅ מתוקן: שני פרמטרים

    # נסיגות
    retrogrades = get_retrograde_planets(transit_chart)

    # בניית הודעה
    message = f"🔮 תחזית אסטרולוגית {now_date.replace('/', '-')} ({now_time}):\n"

    if retrogrades:
        message += "\n🔁 <b>כוכבים בנסיגה:</b>\n"
        for name, explanation in retrogrades:
            message += f"• {name} בנסיגה – {explanation}\n"
    else:
        message += "\n✅ אין כוכבים בנסיגה כרגע.\n"

    if lucky_hours:
        message += "\n🕰️ <b>שעות מזל להיום:</b>\n"
        for hour in lucky_hours:
            message += f"• {hour}\n"
    else:
        message += "\n❌ אין שעות מזל מומלצות היום.\n"

    # שליחה לטלגרם
    token, chat_id = load_secrets()
    send_telegram_message(message, token, chat_id)

if __name__ == "__main__":
    main()
