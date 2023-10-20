import re
from typing import Tuple, Optional


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


RANGE_CODE_PATTERN = re.compile(r'(^(\'?[\w ]+\'?)!|^)\$?([A-Z]+)\$?('
                                r'\d+):\$?([A-Z]+)\$?(\d+)$')


def parse_range_code(text: str) -> Tuple[Optional[str], Tuple[str, int], Tuple[str, int]]:
    result = RANGE_CODE_PATTERN.match(text)
    if result:
        sheet_name = result.group(2)
        left_char = result.group(3)
        left_row = int(result.group(4))
        right_char = result.group(5)
        right_row = int(result.group(6))
        return sheet_name, (left_char, left_row), (right_char, right_row)
    raise ValueError()
