from datetime import date, timedelta


FOUNDING_WEEK_START = date(2026, 7, 13)


def get_week_start(day):
    return day - timedelta(days=day.weekday())


def get_week_number(day):
    week_start = get_week_start(day)
    days_since_founding_week = (week_start - FOUNDING_WEEK_START).days
    return days_since_founding_week // 7
