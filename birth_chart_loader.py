from astro_utils import create_chart  # שם הפונקציה כפי שמופיע אצלך

def load_birth_chart(date_str, time_str, location_str):
    """
    טוען מפת לידה לפי תאריך, שעה ומיקום.
    """
    return create_chart(date_str, time_str, location_str)

def generate_birth_report(birth_chart):
    """
    יוצר דו״ח קצר של מיקומי כוכבים במפת הלידה.
    """
    report = []
    for obj in birth_chart.objects:
        if not hasattr(obj, 'sign'):
            continue
        report.append(f"{obj} ב־{obj.sign} {obj.signlon}")
    return report


