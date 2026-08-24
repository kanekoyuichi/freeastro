from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo


def local_to_utc(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    tz_str: str,
) -> datetime:
    """ローカル日時を UTC の aware datetime に変換する"""
    tz = ZoneInfo(tz_str)
    local_dt = datetime(year, month, day, hour, minute, tzinfo=tz)
    return local_dt.astimezone(ZoneInfo("UTC"))
