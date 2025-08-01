def generate_birth_report(birth_chart):
    report = []
    for obj in birth_chart.objects:
        if not hasattr(obj, 'sign'):
            continue
        report.append(f"{obj} ב־{obj.sign} {obj.signlon}")
    return report
