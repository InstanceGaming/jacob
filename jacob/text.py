import re
from typing import Union, Optional
from urllib.parse import quote
import unicodedata


def format_binary_literal(ba: Union[bytearray, bytes]) -> str:
    if isinstance(ba, bytes):
        ba = bytearray(ba)
    return ' '.join([format(b, '08b') for b in ba])


def conditional(msg, cond=False, paren=False, prefix=' ', postfix='') -> str:
    if msg is not None or cond:
        if paren:
            return f'{prefix}({msg}){postfix}'
        return f'{prefix}{msg}{postfix}'
    return ''


def format_byte_size(size: int, suffix='B') -> str:
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size) < 1024.0:
            return f'{size:.2f}{unit}{suffix}'
        size /= 1024.0
    return f'{size:.2f}Yi{suffix}'


def sentence_case(txt) -> Optional[str]:
    if not txt:
        return None
    if not isinstance(txt, str):
        txt = str(txt)
    return txt[0].upper() + txt[1:]


def wrap(text, width) -> str:
    def _generator():
        for line in text.splitlines(True):  # True keeps trailing linebreaks
            max_width = min((line.endswith('\n') and width + 1 or width), width)
            while len(line) > max_width:
                space = line[: max_width + 1].rfind('') + 1
                if space == 0:
                    space = line.find('') + 1
                    if space == 0:
                        yield line
                        line = ''
                        break
                yield '%s\n' % line[: space - 1]
                line = line[space:]
                max_width = min((line.endswith('\n') and width + 1 or width), width)
            if line:
                yield line

    return ''.join(_generator())


normalize_newlines_pattern = re.compile(r'\r\n|\r')


def normalize_newlines(raw) -> str:
    return re.sub(normalize_newlines_pattern, '\n', raw)


smart_split_pattern = re.compile(r'''((?:[^\s'"]*(?:(?:"(?:[^"\\]|\\.)*" | '(?:[^'\\]|\\.)*')[^\s'"]*)+) | \S+)''')


def smart_split(text) -> str:
    for bit in smart_split_pattern.finditer(str(text)):
        yield bit[0]


def unescape_string_literal(s) -> str:
    if not s or s[0] not in "\"'" or s[-1] != s[0]:
        raise ValueError(f'{s}" is not a string literal')
    qt = s[0]
    return s[1:-1].replace(r'\%s' % qt, qt).replace(r'\\', '\\')


def slugify(value, allow_unicode=False) -> str:
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = (
            unicodedata.normalize('NFKD', value)
            .encode('ascii', 'ignore')
            .decode('ascii')
        )
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def clean_text(v) -> Optional[str]:
    if v is not None:
        stripped = str(v).strip().replace('\n', ' ').replace('\t', ' ')
        if stripped:
            return ' '.join(stripped.split())
    return None


def escape_uri_path(path):
    """
    Escape the unsafe characters from the path portion of a Uniform Resource
    Identifier (URI).
    """
    # These are the "reserved" and "unreserved" characters specified in RFC
    # 3986 Sections 2.2 and 2.3:
    #   reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" | "$" | ","
    #   unreserved  = alphanum | mark
    #   mark        = "-" | "_" | "." | "!" | "~" | "*" | "'" | "(" | ")"
    # The list of safe characters here is constructed subtracting ";", "=",
    # and "?" according to RFC 3986 Section 3.3.
    # The reason for not subtracting and escaping "/" is that we are escaping
    # the entire path, not a path segment.
    return quote(path, safe="/:@&+$,-_.!~*'()")


def filepath_to_uri(path):
    """Convert a file system path to a URI portion that is suitable for
    inclusion in a URL.

    Encode certain chars that would normally be recognized as special chars
    for URIs. Do not encode the ' character, as it is a valid character
    within URIs. See the encodeURIComponent() JavaScript function for details.
    """
    if path is None:
        return path
    # I know about `os.sep` and `os.altsep` but I want to leave
    # some flexibility for hard coding separators.
    return quote(str(path).replace("\\", "/"), safe="/~!*()'")
