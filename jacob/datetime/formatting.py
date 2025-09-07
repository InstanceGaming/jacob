import platform
from typing import Tuple, Optional
from datetime import datetime, timedelta
from jacob.datetime.constants import (
    NS_IN_US,
    US_IN_MS,
    DAYS_IN_WEEK,
    HOURS_IN_DAY,
    MS_IN_SECOND,
    MONTHS_IN_YEAR,
    SECONDS_IN_DAY,
    WEEKS_IN_MONTH,
    MINUTES_IN_HOUR,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE
)


def format_time_unit(v,
                     suffix,
                     pad_char='0',
                     padding=1,
                     precision=2,
                     divisor=None,
                     next_formatter=None):
    if v is None:
        return None
    if v < 0:
        raise ValueError(f'cannot format negative time value ({v})')
    if divisor is None or (divisor is not None and v < divisor):
        if isinstance(v, float):
            return f'{v:{pad_char}{padding}.{precision}f}{suffix}'
        else:
            return f'{v:{pad_char}{padding}}{suffix}'
    else:
        if next_formatter is not None:
            return next_formatter(v / divisor,
                                  pad_char=pad_char,
                                  padding=padding,
                                  precision=precision)
        else:
            raise ValueError('next formatter not set after time unit '
                             f'"{suffix}" (value {v} > {divisor})')


def format_years(v,
                 pad_char='0',
                 padding=1,
                 precision=2,
                 suffix=' years',
                 next_formatter=None):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            next_formatter=next_formatter)


def format_months(v,
                  pad_char='0',
                  padding=1,
                  precision=2,
                  suffix=' months',
                  next_formatter=format_years):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=MONTHS_IN_YEAR,
                            next_formatter=next_formatter)


def format_weeks(v,
                 pad_char='0',
                 padding=1,
                 precision=2,
                 suffix=' weeks',
                 next_formatter=format_months):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=WEEKS_IN_MONTH,
                            next_formatter=next_formatter)


def format_days(v,
                pad_char='0',
                padding=1,
                precision=2,
                suffix='d',
                next_formatter=format_weeks):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=DAYS_IN_WEEK,
                            next_formatter=next_formatter)


def format_hours(v,
                 pad_char='0',
                 padding=1,
                 precision=2,
                 suffix='h',
                 next_formatter=format_days):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=HOURS_IN_DAY,
                            next_formatter=next_formatter)


def format_minutes(v,
                   pad_char='0',
                   padding=1,
                   precision=2,
                   suffix='m',
                   next_formatter=format_hours):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=MINUTES_IN_HOUR,
                            next_formatter=next_formatter)


def format_seconds(v,
                   pad_char='0',
                   padding=1,
                   precision=2,
                   suffix='s',
                   next_formatter=format_minutes):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=SECONDS_IN_MINUTE,
                            next_formatter=next_formatter)


def format_ms(v,
              pad_char='0',
              padding=1,
              precision=2,
              suffix='ms',
              next_formatter=format_seconds):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=MS_IN_SECOND,
                            next_formatter=next_formatter)


def format_us(v,
              pad_char='0',
              padding=1,
              precision=2,
              suffix='us',
              next_formatter=format_ms):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=US_IN_MS,
                            next_formatter=next_formatter)


def format_ns(v,
              pad_char='0',
              padding=1,
              precision=2,
              suffix='ns',
              next_formatter=format_us):
    return format_time_unit(v,
                            suffix,
                            pad_char=pad_char,
                            padding=padding,
                            precision=precision,
                            divisor=NS_IN_US,
                            next_formatter=next_formatter)


def format_timedelta(td: Optional[timedelta], prefix=None):
    prefix = prefix if not None else ''
    if td is not None:
        return f'{prefix}{format_seconds(td.total_seconds())}'
    return None


def format_dhms(seconds) -> Tuple[int, int, int, int]:
    if seconds < 0:
        raise ValueError(f'cannot format negative seconds ({seconds})')
    
    days = seconds // SECONDS_IN_DAY
    seconds %= SECONDS_IN_DAY
    
    hours = seconds // SECONDS_IN_HOUR
    seconds %= SECONDS_IN_HOUR
    
    minutes = seconds // SECONDS_IN_MINUTE
    seconds %= SECONDS_IN_MINUTE
    
    seconds = seconds
    
    return days, hours, minutes, seconds


def compact_datetime(dt: datetime, tz=None) -> str:
    if platform.system() == 'Windows':
        no_pad_char = '#'
    else:
        no_pad_char = '-'
    
    now = datetime.now(tz)
    time_part = dt.time()
    date_part = dt.date()
    
    if time_part.minute == 0:
        time_fmt = f'%{no_pad_char}I%p'
    else:
        time_fmt = f'%{no_pad_char}I:%M%p'
    
    time_text = time_part.strftime(time_fmt).lower()
    date_text = ''
    year_text = ''
    
    if date_part is not None:
        if date_part != now.date():
            date_text = date_part.strftime(f'%b %{no_pad_char}d')
            year_part = date_part.year
            if year_part != now.year:
                year_text = f', {year_part} '
            else:
                date_text += ' '
    
    return f'{date_text}{year_text}{time_text}'
