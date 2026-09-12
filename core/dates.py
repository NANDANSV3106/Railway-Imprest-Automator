"""Month/day arithmetic used across the app."""
import calendar

_MONTH_INDEX = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4,
    "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8,
    "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12,
}


def get_days_in_month(month_name, year):
    """Return (days_in_month, month_index) for a month name + year."""
    m_idx = _MONTH_INDEX[month_name.upper()]
    return calendar.monthrange(int(year), m_idx)[1], m_idx
