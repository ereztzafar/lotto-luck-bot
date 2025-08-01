from astro_utils import calculate_chart  # ודא שהקובץ astro_utils.py כולל פונקציה בשם calculate_chart

def load_birth_chart(date_str, time_str, location_str):
    """
    טוען מפת לידה לפי תאריך, שעה ומיקום.
    פרמטרים:
        date_str: מחרוזת תאריך בפורמט YYYY-MM-DD
        time_str: מחרוזת שעה בפורמט HH:MM
        location_str: מיקום כתובת/עיר
    מחזיר:
        birth_chart (אובייקט של מפת לידה)
    """
    return calculate_chart(date_str, time_str, location_str)

def generate_birth_report(birth_chart):
    """
    מחזיר רשימה של תיאור כוכבים לפי מפת לידה נתונה.
    """
    report = []
    for obj in birth_chart.objects:
        if not hasattr(obj, 'sign'):
            continue
        report.append(f"{obj} ב־{obj.sign} {obj.signlon}")
    return report

