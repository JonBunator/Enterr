from collections import namedtuple
from datetime import timedelta

def timedelta_to_parts(td: timedelta):
    """
    Converts a timedelta object into a named tuple with days, hours, minutes, and seconds.
    Parameters:
    - td (timedelta): The timedelta object to convert.
    Returns:
    - NamedTuple: A named tuple with days, hours, minutes, and seconds.
    """
    # Define the named tuple structure
    TimeParts = namedtuple("TimeParts", ["days", "hours", "minutes", "seconds"])

    # Extract components
    days = td.days
    total_seconds = td.seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return TimeParts(days=days, hours=hours, minutes=minutes, seconds=seconds)


def compare_urls(url1: str, url2: str) -> bool:
    """
    Compares two url strings. Returns True if they match.
    """
    if url1.endswith("/"):
        url1 = url1[:-1]
    if url2.endswith("/"):
        url2 = url2[:-1]
    return url1 == url2

