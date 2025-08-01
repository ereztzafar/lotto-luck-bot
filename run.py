import os
import datetime
from astro_utils import create_chart
from birth_chart_loader import load_birth_chart
from daily_forecast import find_lucky_hours
from telegram_sender import send_telegram_message, load_secrets
from flatlib import const

def get_retrograde_planets(transit_chart):
    planets_to_check = [
        const.MERCURY, const.VENUS, const.MARS,
        const.JUPITER, const.SATURN,
        const.URANUS, const.NEPTUNE, const.PLUTO
    ]
    retrogrades = []
    for p in planets_to_check:
        planet = transit_chart.get(p)
        if planet.retrograde:
            retrogrades.append(planet)
    return retrogrades

def main():
    # פרטי הלידה שלך
    birth_date = '1970/11/22'  # פורמט flatlib
    birth_time = '06:00'
    birth_location = '32n5,34e53'  # פתח תקווה

    # טעינת מפת לידה
    birth_chart = create_chart(birth_date, birth_time, birth_location)

    # מפת טרנזיט נוכחית
    now = datetime.datetime.now()
    now_date = now.strftime('%Y/%m/%d')
    now_time = now.strftime('%H:%M')
    transit_chart = create_chart(now_date, now_time, birth_location)

    # חישוב שעות מזל
    lucky_hours = find_lucky_hours(birth_chart, transit_chart)

    # זיהוי נסיגות
    retrogrades = get_retrograde_planets(transit_chart)

    # בניית הודעה
    message = f"🔮 תחזית אסטרולוגית {now_date.replace('/', '-')} ({now_time}):\n"

    # נסיגות
    if retrogrades:
        message += "\n🔁 <b>כוכבים בנסיגה:</b>\n"
        for p in retrogrades:
            message += f"• {p.name} בנסיגה\n"
    else:
        message += "\n✅ אין כוכבים בנסיגה כרגע.\n"

    # שעות מזל
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
