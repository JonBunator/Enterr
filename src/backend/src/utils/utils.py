from collections import namedtuple
from datetime import timedelta


def edit_timedelta(existing_timedelta: timedelta, days=None, hours=None, minutes=None) -> timedelta:
    """
    Edits the days, hours, and minutes of an existing timedelta object.

    Parameters:
    - existing_timedelta (timedelta): The current timedelta object to be modified.
    - days (Optional[int]): The new days value to set, or None to retain the existing value.
    - hours (Optional[int]): The new hours value to set, or None to retain the existing value.
    - minutes (Optional[int]): The new minutes value to set, or None to retain the existing value.

    Returns:
    - timedelta: The modified timedelta object.
    """
    days, hours, minutes, seconds = timedelta_to_parts(existing_timedelta)

    new_days = days if days is not None else days
    new_hours = hours if hours is not None else hours
    new_minutes = minutes if minutes is not None else minutes

    return timedelta(days=new_days, hours=new_hours, minutes=new_minutes)


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
