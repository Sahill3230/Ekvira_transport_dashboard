from datetime import datetime, date, time

def parse_date(date_str):
    """Safely parses string to date object."""
    if not date_str:
        return None
    if isinstance(date_str, (date, datetime)):
        return date_str
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def parse_time(time_str):
    """Safely parses string to time object."""
    if not time_str:
        return None
    if isinstance(time_str, time):
        return time_str
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return None

def format_percentage(val):
    """Formats numeric value to percentage string."""
    try:
        return f"{float(val):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"
