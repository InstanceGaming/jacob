from time import perf_counter_ns


def micros() -> int:
    return perf_counter_ns() // 1000


def millis() -> int:
    return perf_counter_ns() // 1000000


def seconds() -> int:
    return millis() // 1000


def minutes() -> int:
    return seconds() // 60


def hours() -> int:
    return minutes() // 60


def days() -> int:
    return hours() // 24


_TIMING_FUNCS = [micros, millis, seconds, minutes, hours, days]
