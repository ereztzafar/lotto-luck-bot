import time
import subprocess
from datetime import datetime

# שעות הפעלה בפורמט 24 שעות
TARGET_HOURS = [6, 9, 12, 15, 18, 21]

def already_ran_this_hour(last_run_hour):
    current_hour = datetime.now().hour
    return last_run_hour == current_hour

def run_lotto_bot():
    print("🚀 מריץ תחזית אסטרולוגית...")
    subprocess.run(["python3", "lotto_astrology_bot.py"])

if __name__ == "__main__":
    last_run_hour = None
    while True:
        now = datetime.now()
        hour = now.hour

        if hour in TARGET_HOURS and not already_ran_this_hour(last_run_hour):
            run_lotto_bot()
            last_run_hour = hour
        else:
            print(f"⌛ {now.strftime('%H:%M')} – ממתין לשעה מתאימה...")

        time.sleep(60)  # בדיקה כל דקה
