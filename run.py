# run.py

from birth_chart_loader import load_birth_chart
from daily_forecast import generate_daily_forecast
from telegram_sender import send_forecast_to_telegram

def main():
    print("\U0001F3AF מריץ את בוט המזל האסטרולוגי...")

    # טוען נתוני לידה מקובץ birth_chart.json
    natal_chart = load_birth_chart()
    if not natal_chart:
        print("❌ לא ניתן לטעון את מפת הלידה.")
        return

    # הפקת תחזית יומית לפי נתוני הלידה
    forecast_message = generate_daily_forecast(natal_chart)

    # שליחת התחזית לטלגרם
    send_forecast_to_telegram(forecast_message)

    print("✅ התחזית נשלחה בהצלחה!")

if __name__ == "__main__":
    main()
