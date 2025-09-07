from time import perf_counter_ns
from jacob.datetime.constants import (
    NS_IN_US,
    US_IN_MS,
    HOURS_IN_DAY,
    MS_IN_SECOND,
    MINUTES_IN_HOUR,
    SECONDS_IN_MINUTE
)


def nanos() -> int:
    return perf_counter_ns()


def micros() -> int:
    return nanos() // NS_IN_US


def millis() -> int:
    return micros() // US_IN_MS


def seconds() -> int:
    return millis() // MS_IN_SECOND


def minutes() -> int:
    return seconds() // SECONDS_IN_MINUTE


def hours() -> int:
    return minutes() // MINUTES_IN_HOUR


def days() -> int:
    return hours() // HOURS_IN_DAY


TIMING_FUNCS = (nanos, micros, millis, seconds, minutes, hours, days)
