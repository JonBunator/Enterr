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
