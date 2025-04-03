import platform
from typing import Tuple
from datetime import datetime, timedelta


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

            yearpart = date_part.year
            if yearpart != now.year:
                year_text = f', {yearpart} '
            else:
                date_text += ' '

    return f'{date_text}{year_text}{time_text}'


def format_dhms(seconds) -> Tuple[int, int, int, int]:
    seconds_to_minute = 60
    seconds_to_hour = 60 * seconds_to_minute
    seconds_to_day = 24 * seconds_to_hour

    days = seconds // seconds_to_day
    seconds %= seconds_to_day

    hours = seconds // seconds_to_hour
    seconds %= seconds_to_hour

    minutes = seconds // seconds_to_minute
    seconds %= seconds_to_minute

    seconds = seconds

    return days, hours, minutes, seconds


def format_seconds(s):
    if s is not None:
        if s < 60:
            if isinstance(s, float):
                return f'{s:01.2f}s'
            else:
                return f'{s:01d}s'
        elif 60 <= s < 3600:
            minutes = s / 60
            return f'{minutes:01.2f}min'
        else:
            hours = s / 3600
            return f'{hours:01.2f}h'
    return None


def format_ms(ms):
    if ms is not None:
        if ms >= 1000:
            return format_seconds(ms / 1000)
        else:
            if isinstance(ms, float):
                return f'{ms:01.2f}ms'
            else:
                return f'{ms:01d}ms'
    return None


def format_us(us):
    if us is not None:
        if us >= 1000:
            return format_ms(us / 1000)
        else:
            if isinstance(us, float):
                return f'{us:01.2f}us'
            else:
                return f'{us}us'
    return None


def format_ns(ns: int):
    if ns is not None:
        if ns >= 1000:
            return format_us(ns / 1000)
        else:
            return f'{ns:01d}ns'
    return None


def format_timedelta(td: timedelta, prefix=None, format_spec=None):
    prefix = prefix if not None else ''
    format_spec = format_spec if format_spec is not None else '02.2f'

    if td is not None:
        seconds = td.total_seconds()
        if seconds < 60:
            return prefix + format(seconds, format_spec) + ' seconds'
        elif 60 <= seconds < 3600:
            return prefix + format(seconds / 60, format_spec) + ' minutes'
        elif 3600 <= seconds < 86400:
            return prefix + format(seconds / 3600, format_spec) + ' hours'
        elif 86400 <= seconds:
            return prefix + format(seconds / 86400, format_spec) + ' days'
    return None
