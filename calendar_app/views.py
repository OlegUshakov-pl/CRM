import calendar
from datetime import date, datetime, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]


def _build_month_data(year, month, today):
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
    return {
        'month': month,
        'year': year,
        'month_name': MONTH_NAMES[month - 1],
        'month_name_short': MONTH_NAMES[month - 1][:3],
        'weeks': weeks,
    }


def _add_months(year, month, delta):
    total = month + delta
    y = year + (total - 1) // 12
    m = (total - 1) % 12 + 1
    return y, m


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

    months_data = []
    for delta in range(3):
        y, m = _add_months(year, month, delta)
        months_data.append(_build_month_data(y, m, today))

    prev_y, prev_m = _add_months(year, month, -1)
    next_y, next_m = _add_months(year, month, 1)

    return render(request, 'calendar_app/calendar.html', {
        'months_data': months_data,
        'base_month': month,
        'base_year': year,
        'prev_month': prev_m,
        'prev_year': prev_y,
        'next_month': next_m,
        'next_year': next_y,
        'months': [(i + 1, MONTH_NAMES[i]) for i in range(12)],
        'years': list(range(year - 10, year + 11)),
        'today': today,
    })
