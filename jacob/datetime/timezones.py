from datetime import timedelta
from time import localtime, timezone, altzone


def get_utc_offset() -> float:
    offset = timezone if (localtime().tm_isdst == 0) else altzone
    offset = offset / 60 / 60 * -1
    return offset


def get_utc_delta() -> timedelta:
    utc_offset = get_utc_offset()
    utc_delta = timedelta(hours=utc_offset)
    return utc_delta
