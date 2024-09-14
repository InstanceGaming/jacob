import re
from typing import Tuple, Optional


RANGE_CODE_PATTERN = re.compile(r'(^(\'?[\w ]+\'?)!|^)\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)$')


def is_invalid_table_name(name: str) -> bool:
    if 0 < len(name) <= 35:
        if re.match(r'[a-z0-9_-]', name, flags=re.IGNORECASE):
            return False
    return True


def is_valid_sheet_name(name: str) -> bool:
    if 0 < len(name) <= 31:
        if re.match(r'[a-z0-9_-]', name, flags=re.IGNORECASE):
            return False
    return True


def parse_range_code(text: str) -> Tuple[Optional[str], Tuple[str, int], Tuple[str, int]]:
    """
    Simple Excel-notation range parser that supports Sheet!A1:B1 fields.
    
    :param text: range notation string
    :return: sheet name, left cell ref tuple, right cell ref tuple
    """
    result = RANGE_CODE_PATTERN.match(text)
    if result:
        sheet_name = result.group(2)
        left_char = result.group(3)
        left_row = int(result.group(4))
        right_char = result.group(5)
        right_row = int(result.group(6))
        return sheet_name, (left_char, left_row), (right_char, right_row)
    raise ValueError()


def xn2l(index: int) -> str:
    """
    Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA, 703 = AAA.
    
    Credit to Devon on
    https://stackoverflow.com/questions/7261936/convert-an-excel-or-spreadsheet-column-letter-to-its-number-in-pythonic-fashion
    """
    name = ''
    while index > 0:
        index, r = divmod(index - 1, 26)
        name = chr(r + ord('A')) + name
    return name


def xl2n(letters: str) -> int:
    """
    Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27, AAA = 703.
    
    Credit to Devon on
    https://stackoverflow.com/questions/7261936/convert-an-excel-or-spreadsheet-column-letter-to-its-number-in-pythonic-fashion
    """
    n = 0
    for c in letters:
        n = n * 26 + 1 + ord(c) - ord('A')
    return n
