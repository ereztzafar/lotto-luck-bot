import os
import datetime
from astro_utils import create_chart
from birth_chart_loader import load_birth_chart
from daily_forecast import find_lucky_hours
from telegram_sender import send_telegram_message, load_secrets

def main():
    # פרטי הלידה שלך (שמורים מראש בקוד או בקובץ)
    birth_date = '1970-11-22'
    birth_time = '06:00'
    birth_location = '32.0840,34.8878'  # פתח תקווה

    # טעינת מפת לידה
    birth_chart = create_chart(birth_date, birth_time, birth_location)

    # מפת טרנזיט נוכחית
    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    now_time = now.strftime('%H:%M')
    transit_chart = create_chart(now_date, now_time, birth_location)

    # ניתוח שעות מזל
    lucky_hours = find_lucky_hours(birth_chart, transit_chart)

    # בניית הודעה
    message = f"🔮 תחזית אסטרולוגית {now_date} ({now_time}):\n"
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
