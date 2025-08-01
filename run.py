import datetime
import json
import os
from flatlib.geopos import GeoPos
from astro_utils import create_chart
from birth_chart_loader import load_birth_chart
from daily_forecast import find_lucky_hours
from telegram_sender import send_telegram_message, load_secrets
from retrograde_generator import generate_retrogrades  # ✅ קריאה למחולל נסיגות

# ✅ הפעלת מחולל נסיגות כל פעם שהבוט רץ
today = datetime.date.today()
future = today + datetime.timedelta(days=30)
generate_retrogrades(today, future)

RETRO_FILE = "retrogrades.json"

def load_retrogrades_for_today():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(RETRO_FILE):
        return []

    with open(RETRO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(today, [])

def main():
    # פרטי הלידה שלך
    birth_date = '1970/11/22'
    birth_time = '06:00'
    birth_location = GeoPos("32n5", "34e53")

    # תאריך נוכחי
    now = datetime.datetime.now()
    now_date = now.strftime('%Y/%m/%d')
    now_date_key = now.strftime('%Y-%m-%d')
    now_time = now.strftime('%H:%M')

    # יצירת מפות
    birth_chart = create_chart(birth_date, birth_time, birth_location)
    transit_chart = create_chart(now_date, now_time, birth_location)

    # שליפת שעות מזל
    lucky_hours = find_lucky_hours(birth_chart, transit_chart)

    # שליפת נסיגות מהקובץ
    retrogrades = load_retrogrades_for_today()

    # בניית הודעה
    message = f"🔮 תחזית אסטרולוגית {now_date_key} ({now_time}):\n"

    if retrogrades:
        message += "\n🔁 <b>כוכבים בנסיגה:</b>\n"
        for r in retrogrades:
            message += f"• {r['planet']} בנסיגה – {r['explanation']}\n"
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
