from birth_chart import get_birth_chart
from lotto_bot import send_telegram_message
from flatlib.geopos import GeoPos
from datetime import datetime

# פרטי הלידה שלך
BIRTH_DATE = '1970/11/22'
BIRTH_TIME = '06:00'
BIRTH_PLACE = GeoPos('32n05', '34e53')  # פתח תקווה

def start_forecast():
    now = datetime.now()
    message = f"📆 התחזית האסטרולוגית להיום - {now.strftime('%d/%m/%Y')}\n"
    message += "מתחילים לחשב את הטרנזיטים והשפעות הכוכבים לפי מפת הלידה שלך... 🔭"

    print(message)
    send_telegram_message(message)

    # יצירת מפת לידה לפי פרטי הלידה
    chart = get_birth_chart(BIRTH_DATE, BIRTH_TIME, BIRTH_PLACE)
    print("✅ מפת לידה נטענה בהצלחה.")

if __name__ == "__main__":
    start_forecast()

