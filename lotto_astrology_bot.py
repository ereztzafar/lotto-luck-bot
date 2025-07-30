def get_astrology_forecast():
    tz = get_timezone()
    now_utc = datetime.utcnow().strftime('%Y/%m/%d %H:%M')
    dt = Datetime(now_utc.split()[0], now_utc.split()[1], tz)

    # השעה האמיתית לפי ישראל
    now_local = datetime.now(timezone('Asia/Jerusalem')).strftime('%H:%M:%S')

    # יצירת רשימת כוכבים
    objects = [
        const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
        const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
    ]

    try:
        chart = Chart(dt, BIRTH_PLACE, IDs=objects)
    except Exception as e:
        return f"❌ שגיאה ביצירת מפת לידה: {e}"

    names = {
        const.SUN: "☀️ שמש",
        const.MOON: "🌙 ירח",
        const.MERCURY: "☿ מרקורי",
        const.VENUS: "♀ ונוס",
        const.MARS: "♂ מארס",
        const.JUPITER: "♃ צדק",
        const.SATURN: "♄ שבתאי",
        const.URANUS: "♅ אורנוס",
        const.NEPTUNE: "♆ נפטון",
        const.PLUTO: "♇ פלוטו",
    }

    forecast = f"🔮 תחזית אסטרולוגית ל־{now_local} (שעון ישראל):\n\n"
    signs = {}
    reasons = []

    for obj in objects:
        planet = chart.get(obj)
        deg = int(planet.lon)
        min = int((planet.lon - deg) * 60)
        forecast += f"{names[obj]} במזל {planet.sign} {deg}°{min:02d}′\n"
        signs[obj] = planet.sign

    # ניתוח חכם עם סיבות מפורטות
    score = 0

    if signs[const.JUPITER] in ['Taurus', 'Pisces', 'Cancer']:
        score += 2
        reasons.append(f"♃ צדק במזל {signs[const.JUPITER]} – מזל טוב להצלחה וכסף (+2)")

    if signs[const.VENUS] in ['Leo', 'Libra']:
        score += 1
        reasons.append(f"♀ ונוס במזל {signs[const.VENUS]} – מגביר יצירתיות ומשיכה למזל (+1)")

    if signs[const.MOON] in ['Scorpio', 'Capricorn']:
        score -= 1
        reasons.append(f"🌙 ירח במזל {signs[const.MOON]} – עלול להכניס מתחים פנימיים (-1)")

    if signs[const.SATURN] in ['Aquarius', 'Capricorn']:
        score -= 1
        reasons.append(f"♄ שבתאי במזל {signs[const.SATURN]} – מגביל ומכביד על מזל אישי (-1)")

    if signs[const.SUN] == 'Sagittarius':
        score += 1
        reasons.append("☀️ שמש במזל קשת – תומך באופטימיות והרפתקנות (+1)")

    if signs[const.MERCURY] in ['Gemini', 'Virgo']:
        score += 1
        reasons.append(f"☿ מרקורי במזל {signs[const.MERCURY]} – חדות שכלית והתמקדות נכונה (+1)")

    if signs[const.URANUS] == 'Aries':
        score += 1
        reasons.append("♅ אורנוס בטלה – מזל פתאומי והפתעות נעימות (+1)")

    if signs[const.PLUTO] == 'Scorpio':
        score += 1
        reasons.append("♇ פלוטו בעקרב – עומק אינטואיטיבי ואומץ לקחת סיכונים (+1)")

    if signs[const.NEPTUNE] == 'Pisces':
        score += 1
        reasons.append("♆ נפטון בדגים – תחושת זרימה והרמוניה פנימית טובה להימורים (+1)")

    # קביעת רמת מזל
    if score >= 4:
        level = "🟢 סיכוי גבוה לזכייה היום!"
    elif 1 <= score < 4:
        level = "🟡 סיכוי בינוני – שווה לנסות חישגד או צ'אנס."
    else:
        level = "🔴 לא מומלץ היום – שמור את הכסף למחר."

    # הרכבת התחזית הסופית
    forecast += "\n\n📌 נימוקים לתחזית:\n" + '\n'.join(f"- {reason}" for reason in reasons)
    forecast += f"\n\n🎲 {level}"

    return forecast.strip()
