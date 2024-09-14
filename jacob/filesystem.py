import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional, Iterable, List
from jacob.text import clean_text
from jacob.types import PathLike


# special file names that cannot be created on Win32 platforms
WIN32_RESERVED_NAMES = (
    'CON',
    'PRN',
    'AUX',
    'NUL',
    'COM1',
    'COM2',
    'COM3',
    'COM4',
    'COM5',
    'COM6',
    'COM7',
    'COM8',
    'COM9',
    'LPT1',
    'LPT2',
    'LPT3',
    'LPT4',
    'LPT5',
    'LPT6',
    'LPT7',
    'LPT8',
    'LPT9'
)


def fix_path(raw_path: Optional[PathLike]) -> Optional[Path]:
    """
    Clean up a path to have all environment variables expanded, the user
    "~" placeholder expanded, and the path slashes normalized.
    :param raw_path: Path() or str
    :return: Cleaned Path or None
    """
    if raw_path is not None:
        return Path(os.path.expandvars(os.path.expanduser(os.path.normpath(raw_path))))
    return None


def fix_paths(paths: Iterable[Optional[PathLike]]) -> List[Optional[Path]]:
    """
    Call fix_path() on a collection of paths.
    """
    rv = []
    for path in paths:
        rv.append(fix_path(path))
    return rv


def ensure_trailing_slash(path: os.PathLike) -> str:
    """
    Make sure a given path ends with the system path separator character.
    :param path: original path-like object
    :return: path string with slash at the end
    """
    path = str(path)
    if path.endswith(os.sep):
        return path
    else:
        return f'{path}{os.sep}'


def is_dir_writeable(path):
    """
    Confirm if a directory is writable.
    :param path: Path to presumably a directory.
    :return: True if it is a directory and writable.
    """
    
    try:
        if not os.path.isdir(path):
            return False
        testfile = tempfile.TemporaryFile(dir=path)
        testfile.close()
        return True
    except OSError:
        return False


def remove_dirs(name, stop_dir=None):
    """removedirs(name)
    Super-rmdir; remove a leaf directory and all empty intermediate
    ones.  Works like rmdir except that, if the leaf directory is
    successfully removed, directories corresponding to rightmost path
    segments will be pruned away until either the whole path is
    consumed or an error occurs.  Errors during this latter phase are
    ignored -- they generally mean that a directory was not empty.

    If stop_dir is given, will stop when head equals stop_dir,
    preventing stop_dir and up from being removed.
    """
    stop_head = None
    if stop_dir:
        stop_head, _ = os.path.split(os.path.join(stop_dir, ''))
        if name == stop_head:
            return

    os.rmdir(name)

    head, tail = os.path.split(name)
    if not tail:
        head, tail = os.path.split(head)

    while head and tail:
        if head == stop_head:
            break
        try:
            os.rmdir(head)
        except OSError:
            break
        head, tail = os.path.split(head)


def coerce_filename(unsanitized, allow_spaces=False) -> Optional[str]:
    """
    Make a valid filename out of untrusted text, discarding invalid characters.
    
    :param unsanitized: Untrusted text to make a filename out of.
    :param allow_spaces: Allow spaces in the resulting file name.
    :return: Sanitized filename.
    """
    cleaned = clean_text(unsanitized)
    if cleaned is not None:
        if not allow_spaces:
            cleaned = cleaned.replace(' ', '_')
        cleaned = re.sub(r'(?u)[^-\w.]', '', cleaned)
        
        if sys.platform == 'win32':
            if cleaned in WIN32_RESERVED_NAMES:
                raise ValueError('reserved platform filename')

        return cleaned
    return None


def ensure_extension(original: PathLike, extension: str) -> Path:
    """
    Append a file extension if not present.
    
    :param original: Path() or str of a filename.
    :param extension: Extension to ensure is present in filename.
    :return: Filename with extension appended.
    """
    original = Path(original)
    if not original.suffix or original.suffixes[-1] != extension:
        return original.with_suffix(extension)


def simplify_paths(paths: List[Path]) -> None:
    """
    Process a list of relative paths (which are assumed to have a common root)
    to remove paths that would be traversable via each longest, unique path.

    :param paths: List of pathlib.Path() instances to modify in-place.
    """
    
    paths.sort(key=lambda p: len(p.parts), reverse=True)
    
    i = 0
    while i < len(paths):
        current_path = paths[i]
        j = len(paths) - 1
        while j > 0:
            other_path = paths[j]
            if i != j and current_path.is_relative_to(other_path):
                del paths[j]
            j -= 1
        i += 1
