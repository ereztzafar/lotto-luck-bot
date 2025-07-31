from birth_chart import get_birth_chart
from lotto_bot import send_telegram_message
from flatlib.geopos import GeoPos
from flatlib.datetime import Datetime
from flatlib import const, ephem
from flatlib.chart import Chart
from flatlib import aspects
from datetime import datetime

# פרטי הלידה שלך
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')  # פתח תקווה
TIMEZONE = '+02:00'

def start_forecast():
    now = datetime.now()
    today_str = now.strftime('%d/%m/%Y')

    message = f"📆 התחזית האסטרולוגית להיום - {today_str}\n"
    message += "🔭 מחשב מפת לידה וטרנזיטים...\n"

    send_telegram_message(message)

    # מפת לידה
    birth_chart = get_birth_chart(BIRTH_DATE, BIRTH_TIME, BIRTH_PLACE)

    # מפת טרנזיט של היום
    today_dt = Datetime(now.strftime('%Y/%m/%d'), now.strftime('%H:%M'), TIMEZONE)
    transit_chart = Chart(today_dt, BIRTH_PLACE)

    # בדיקת אספקטים בין מפת הלידה לטרנזיטים
    insights = []
    for obj in birth_chart.objects:
        transit = transit_chart.get(obj.id)
        natal = birth_chart.get(obj.id)

        if not transit or not natal:
            continue

        angle = abs(transit.lon - natal.lon) % 360
        aspect_type = aspects.aspectType(angle)

        if aspect_type in [aspects.CONJUNCTION, aspects.TRINE, aspects.SEXTILE]:
            insights.append(f"✨ {obj.id} בזווית חיובית ({aspect_type}) - פוטנציאל חיובי.")
        elif aspect_type in [aspects.SQUARE, aspects.OPPOSITION]:
            insights.append(f"⚠️ {obj.id} בזווית מאתגרת ({aspect_type}) - שים לב.")

    if not insights:
        insights.append("📌 היום לא נמצאו אספקטים משמעותיים.")

    # שליחת התחזית
    forecast = "\n".join(insights)
    send_telegram_message(f"🪐 התחזית:\n{forecast}")
    print("✅ התחזית נשלחה לטלגרם.")

if __name__ == "__main__":
    start_forecast()
