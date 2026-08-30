from datetime import datetime, timezone

import issoverhead


class FrozenDateTime(datetime):
    current = datetime(2026, 1, 2, 0, 30, tzinfo=timezone.utc)

    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return cls.current.astimezone(tz)
        return cls.current


def test_is_dark_before_sunrise_after_midnight(monkeypatch):
    issoverhead.sunrise_dt = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)
    issoverhead.sunset_dt = datetime(2026, 1, 1, 18, 0, tzinfo=timezone.utc)
    FrozenDateTime.current = datetime(2026, 1, 2, 0, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(issoverhead, "datetime", FrozenDateTime)

    assert issoverhead.is_dark() is True


def test_is_dark_is_false_during_day(monkeypatch):
    issoverhead.sunrise_dt = datetime(2026, 1, 2, 6, 0, tzinfo=timezone.utc)
    issoverhead.sunset_dt = datetime(2026, 1, 2, 18, 0, tzinfo=timezone.utc)
    FrozenDateTime.current = datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(issoverhead, "datetime", FrozenDateTime)

    assert issoverhead.is_dark() is False


def test_is_dark_requires_data():
    issoverhead.sunrise_dt = None
    issoverhead.sunset_dt = None

    assert issoverhead.is_dark() is False
