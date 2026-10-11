from datetime import datetime, timezone

import pytest

from dataAccess.database.database import ActionInterval

NOW = datetime(2024, 5, 10, 15, 30, tzinfo=timezone.utc)


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW


@pytest.fixture
def fixed_now(mocker):
    mocker.patch("dataAccess.database.database.datetime", FixedDatetime)


@pytest.mark.parametrize(
    "date_start, date_end, time_start, time_end",
    [
        (2880, 1440, None, None),  # date end before date start
        (1440, 1440, 120, 60),  # allowed time end before allowed time start
        (100, None, 60, 120),  # time window requires full days
        (1440, 1500, 60, 120),  # time window requires full days (end)
    ],
)
def test_invalid_intervals_raise(date_start, date_end, time_start, time_end):
    with pytest.raises(ValueError):
        ActionInterval(date_start, date_end, time_start, time_end)


@pytest.mark.parametrize(
    "date_start, date_end, time_start, time_end",
    [
        (30, 60, None, None),  # no time window allows any minutes
        (1440, 2880, 60, 120),
        (1440, None, None, None),
    ],
)
def test_valid_intervals(date_start, date_end, time_start, time_end):
    ActionInterval(date_start, date_end, time_start, time_end)


def test_random_action_datetime_full_days_uses_time_window(mocker, fixed_now):
    randint = mocker.patch(
        "dataAccess.database.database.randint", side_effect=[1440, 60]
    )
    interval = ActionInterval(1440, 2880, 60, 120)

    result = interval.get_random_action_datetime()

    # next day at 01:00 (naive UTC)
    assert result == datetime(2024, 5, 11, 1, 0)
    assert randint.call_args_list == [mocker.call(1440, 2880), mocker.call(60, 120)]


def test_random_action_datetime_minutes_offset(mocker, fixed_now):
    mocker.patch("dataAccess.database.database.randint", return_value=45)
    interval = ActionInterval(30, 60, None, None)

    result = interval.get_random_action_datetime()

    assert result == datetime(2024, 5, 10, 16, 15, tzinfo=timezone.utc)
