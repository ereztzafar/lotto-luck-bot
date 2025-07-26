import ephem
import os
import requests
from datetime import datetime

# טוען את הטוקן וה-Chat ID מתוך משתני סביבה (Secrets)
def load_secrets():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise Exception("❌ חסר TELEGRAM_TOKEN או TELEGRAM_CHAT_ID בסודות של GitHub")
    return token, chat_id

# שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

# תחזית אסטרולוגית לפי מיקום כוכבים
def get_astrology_forecast():
    now = datetime.utcnow()
    sun = ephem.Sun(now)
    moon = ephem.Moon(now)
    jupiter = ephem.Jupiter(now)

    sun_sign = ephem.constellation(sun)[1]
    moon_sign = ephem.constellation(moon)[1]
    jup_sign = ephem.constellation(jupiter)[1]

    forecast = f"""🔮 תחזית אסטרולוגית לשעה {now.strftime('%H:%M')} UTC:

☀️ השמש במזל {sun_sign}
🌙 הירח במזל {moon_sign}
♃ יופיטר במזל {jup_sign}
"""

    if moon_sign == 'Virgo' and jup_sign in ['Taurus', 'Cancer']:
        forecast += "\n💡 זהו זמן מבורך! מומלץ למלא לוטו או חישגד."
    elif moon_sign == 'Scorpio':
        forecast += "\n⚠️ ייתכנו מתחים פנימיים – פעל בזהירות."
    elif jup_sign == 'Leo':
        forecast += "\n🎉 יופיטר מעניק דחיפה חיובית – נצל את ההזדמנות!"
    else:
        forecast += "\n🕰 לא זוהתה השפעה מובהקת כרגע – המתן לשעה אחרת."

    return forecast

if __name__ == "__main__":
    message = get_astrology_forecast()
    send_telegram_message(message)
