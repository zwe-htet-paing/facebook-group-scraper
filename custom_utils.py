import codecs
import re
import dateparser
from datetime import datetime, timedelta
import calendar
from typing import Optional

month = (
    r"Jan(?:uary)?|"
    r"Feb(?:ruary)?|"
    r"Mar(?:ch)?|"
    r"Apr(?:il)?|"
    r"May|"
    r"Jun(?:e)?|"
    r"Jul(?:y)?|"
    r"Aug(?:ust)?|"
    r"Sep(?:tember)?|"
    r"Oct(?:ober)?|"
    r"Nov(?:ember)?|"
    r"Dec(?:ember)?"
)
day_of_week = r"Mon|" r"Tue|" r"Wed|" r"Thu|" r"Fri|" r"Sat|" r"Sun"
day_of_month = r"\d{1,2}"
specific_date_md = f"(?:{month}) {day_of_month}" + r"(?:,? \d{4})?"
specific_date_dm = f"{day_of_month} (?:{month})" + r"(?:,? \d{4})?"

date = f"{specific_date_md}|{specific_date_dm}|Today|Yesterday"

hour = r"\d{1,2}"
minute = r"\d{2}"
period = r"AM|PM|"

exact_time = f"(?:{date}) at {hour}:{minute} ?(?:{period})"
relative_time_years = r'\b\d{1,2} yr'
relative_time_months = r'\b\d{1,2} (?:mth|mo)'
relative_time_weeks = r'\b\d{1,2} wk'
relative_time_hours = r"\b\d{1,2} ?h(?:rs?)?"
relative_time_mins = r"\b\d{1,2} ?mins?"
relative_time = f"{relative_time_years}|{relative_time_months}|{relative_time_weeks}|{relative_time_hours}|{relative_time_mins}"

datetime_regex = re.compile(fr"({exact_time}|{relative_time})", re.IGNORECASE)
day_of_week_regex = re.compile(fr"({day_of_week})", re.IGNORECASE)


def parse_datetime(text: str, search=True) -> Optional[datetime]:
    """Looks for a string that looks like a date and parses it into a datetime object.

    Uses a regex to look for the date in the string.
    Uses dateparser to parse the date (not thread safe).

    Args:
        text: The text where the date should be.
        search: If false, skip the regex search and try to parse the complete string.

    Returns:
        The datetime object, or None if it couldn't find a date.
    """
    settings = {
        'RELATIVE_BASE': datetime.today().replace(minute=0, hour=0, second=0, microsecond=0)
    }
    if search:
        time_match = datetime_regex.search(text)
        dow_match = day_of_week_regex.search(text)
        if time_match:
            text = time_match.group(0).replace("mth", "month")
        elif dow_match:
            text = dow_match.group(0)
            today = calendar.day_abbr[datetime.today().weekday()]
            if text == today:
                # Fix for dateparser misinterpreting "last Monday" as today if today is Monday
                return dateparser.parse(text, settings=settings) - timedelta(days=7)

    result = dateparser.parse(text, settings=settings)
    if result:
        return result.replace(microsecond=0)
    return None


if __name__ == "__main__":
    date_string = "13 October at 18:12"
    print(parse_datetime(date_string))