import codecs
import datetime
import locale
from decimal import Decimal
from types import NoneType


def get_system_encoding():
    try:
        encoding = locale.getlocale()[1] or 'ascii'
        codecs.lookup(encoding)
    except LookupError:
        encoding = 'ascii'
    return encoding


locale_encoding_guess = get_system_encoding()


untouched_types = (
    NoneType,
    int,
    float,
    Decimal,
    datetime.datetime,
    datetime.date,
    datetime.time,
)


def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and s in untouched_types:
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    return str(s).encode(encoding, errors)


def punycode(domain):
    return domain.encode('idna').decode('ascii')
