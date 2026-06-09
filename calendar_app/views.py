import calendar
from datetime import date, datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]


@login_required
def calendar_view(request):
    today = date.today()
    year = request.GET.get('year')
    month = request.GET.get('month')

    try:
        year = int(year) if year else today.year
    except (ValueError, TypeError):
        year = today.year

    try:
        month = int(month) if month else today.month
    except (ValueError, TypeError):
        month = today.month

    month = max(1, min(12, month))
    year = max(1900, min(2100, year))

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    weeks = []
    for week in month_days:
        rows = []
        for day in week:
            rows.append({
                'day': day,
                'is_today': day == today.day and month == today.month and year == today.year,
            })
        weeks.append(rows)

    first_day_of_month = date(year, month, 1)

    context = {
        'month': month,
        'year': year,
        'month_name': MONTH_NAMES[month - 1],
        'weeks': weeks,
        'months': [(i + 1, MONTH_NAMES[i]) for i in range(12)],
        'years': list(range(year - 10, year + 11)),
        'today': today,
        'prev_month': first_day_of_month.replace(month=month - 1) if month > 1 else first_day_of_month.replace(year=year - 1, month=12),
        'next_month': first_day_of_month.replace(month=month + 1) if month < 12 else first_day_of_month.replace(year=year + 1, month=1),
    }
    return render(request, 'calendar_app/calendar.html', context)
