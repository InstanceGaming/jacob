import sys
from jacob.datetime.formatting import *
from jacob.text import csl


line_count = 1


def _test_func(func_, *args):
    global line_count
    try:
        print(f'[{line_count:04d}] {func_.__name__}({csl(args)}) = {func_(*args)}')
    except Exception as e:
        print(f'[{line_count:04d}] {func_.__name__}({csl(args)}) = [{type(e).__name__}] {str(e)}')
    line_count += 1


def test_format_x():
    tests = {
        format_ns: 1000,
        format_us: 1000,
        format_ms: 1000,
        format_seconds: 60,
        format_minutes: 60,
        format_hours: 24,
        format_days: 7,
        format_weeks: 4,
        format_months: 12,
        format_years: None
    }
    for func, divisor in tests.items():
        _test_func(func, -1)
        _test_func(func, float(-1))
        _test_func(func, 0)
        _test_func(func, float(0))
        _test_func(func, 1)
        _test_func(func, float(1))
        _test_func(func, sys.maxsize)
        _test_func(func, float(sys.maxsize))
        if divisor is not None:
            _test_func(func, divisor - 1)
            _test_func(func, float(divisor - 1))
            _test_func(func, divisor)
            _test_func(func, float(divisor))
            _test_func(func, divisor + 1)
            _test_func(func, float(divisor + 1))


def test_format_dhms():
    for i in range(-1, SECONDS_IN_HOUR + 1):
        _test_func(format_dhms, i)

test_format_x()
test_format_dhms()
