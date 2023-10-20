from enum import Enum
from typing import Type, Any


def default_enum(et: Type[Enum], value: Any) -> dict:
    rv = {}
    for i in [e.value for e in et]:
        rv.update({i: value})
    return rv


def text_to_enum(et: Type[Enum], v, to_length=None, dash_underscore=True):
    """
    Attempt to return the matching enum next_state based off of
    the text tag of a next_state.

    :param et: enum type
    :param v: string representation of an enum next_state
    :param to_length: only match to this many chars
    :param dash_underscore: make dash equal to underscore character
    :return: enum next_state of type e or None if was None
    :raises ValueError: if text could not be mapped to type
    """
    if v is None:
        return None

    v = v.strip().lower()

    if dash_underscore:
        v = v.replace('-', '_')

    for e in et:
        name = e.name.lower()
        if isinstance(to_length, int):
            if v[0:to_length] == name[0:to_length]:
                return v
        else:
            if v == name:
                return e
    raise ValueError(f'Could not match "{v}" to {str(et)}')
