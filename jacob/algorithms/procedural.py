
#
# Next two functions credit to Devon
# https://stackoverflow.com/questions/7261936/convert-an-excel-or-spreadsheet
# -column-letter-to-its-number-in-pythonic-fashion
#

def xn2l(index: int) -> str:
    """Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA,
    703 = AAA."""
    name = ''
    while index > 0:
        index, r = divmod(index - 1, 26)
        name = chr(r + ord('A')) + name
    return name


def xl2n(letters: str) -> int:
    """Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27,
    AAA = 703."""
    n = 0
    for c in letters:
        n = n * 26 + 1 + ord(c) - ord('A')
    return n
