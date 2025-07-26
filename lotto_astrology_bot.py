import ephem
import json
import requests
from datetime import datetime

# טוען את הטוקן וה-Chat ID מקובץ הסודות
def load_secrets():
    with open("secrets.json", "r") as file:
        data = json.load(file)
        return data["BOT_TOKEN"], data["CHAT_ID"]

# שליחת הודעה לטלגרם
def send_telegram_message(message: str):
    token, chat_id = load_secrets()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"📤 Status: {response.status_code} | {message}")

# פונקציית חיזוי לפי מיקום כוכבים
def get_astrology_forecast():
    now = datetime.utcnow()

    sun = ephem.Sun(now)
    moon = ephem.Moon(now)
    jupiter = ephem.Jupiter(now)

    sun_sign = ephem.constellation(sun)[1]
    moon_sign = ephem.constellation(moon)[1]
    jup_sign = ephem.constellation(jupiter)[1]

    forecast = f"""🔮 תחזית אסטרולוגית לשעה {now.strftime('%H:%M')}:

☀️ השמש במזל {sun_sign}
🌙 הירח במזל {moon_sign}
♃ יופיטר במזל {jup_sign}

"""

    # ניתוח מזל
    if moon_sign == 'Virgo' and jup_sign in ['Taurus', 'Cancer']:
        forecast += "💡 הזמן מבורך! כדאי לבדוק אפשרויות למילוי לוטו או חישגד."
    elif moon_sign == 'Scorpio':
        forecast += "⚠️ ייתכנו מתחים פנימיים – להפעיל שיקול דעת."
    elif jup_sign == 'Leo':
        forecast += "🎉 יופיטר נותן דחיפה – פעל עם ביטחון!"
    else:
        forecast += "🕰 כרגע לא זוהתה השפעה מובהקת – המתן לשעה אחרת."

    return forecast

if __name__ == "__main__":
    msg = get_astrology_forecast()
    send_telegram_message(msg)

