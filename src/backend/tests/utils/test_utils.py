from datetime import datetime, timedelta, timezone

import pytest

from utils.utils import compare_urls, timedelta_to_parts, to_utc_time


@pytest.mark.parametrize(
    "url1, url2, expected",
    [
        ("https://example.com", "https://example.com", True),
        ("https://example.com/", "https://example.com", True),
        ("https://example.com/home", "https://example.com/home/", True),
        ("https://example.com/home", "https://example.com/login", False),
        ("http://example.com", "https://example.com", False),
    ],
)
def test_compare_urls(url1, url2, expected):
    assert compare_urls(url1, url2) is expected


def test_timedelta_to_parts():
    parts = timedelta_to_parts(timedelta(days=1, hours=2, minutes=3, seconds=4))
    assert parts == (1, 2, 3, 4)
    assert parts.days == 1
    assert parts.hours == 2
    assert parts.minutes == 3
    assert parts.seconds == 4


def test_to_utc_time_none():
    assert to_utc_time(None) is None


def test_to_utc_time_naive_becomes_utc():
    result = to_utc_time(datetime(2024, 5, 10, 8, 0))
    assert result == datetime(2024, 5, 10, 8, 0, tzinfo=timezone.utc)


def test_to_utc_time_aware_unchanged():
    tz = timezone(timedelta(hours=2))
    dt = datetime(2024, 5, 10, 8, 0, tzinfo=tz)
    assert to_utc_time(dt) is dt
