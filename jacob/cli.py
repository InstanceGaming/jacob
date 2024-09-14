import re
from enum import Flag, auto
from pathlib import Path
from typing import Iterable, Optional, Any, Type, List, TextIO


class ArgumentMode(Flag):
    SINGLE_VALUE = auto()
    ONE_PLUS_VALUES = auto()
    ZERO_PLUS_VALUES = auto()
    MULTIPLE_VALUES = auto()
    MULTIPLE_DEFINITION = auto()
    FLAG = auto()
    COLLECTOR = auto()


DEFAULT_ARGUMENT_MODE = ArgumentMode.ZERO_PLUS_VALUES


class ArgumentError(Exception):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.unknown_arguments: Optional[List[Argument]] = kwargs.get('unknown_arguments')


class InvalidUsage(ArgumentError):
    pass


class Positioning(ArgumentError):
    pass


class Ambiguity(ArgumentError):
    pass


class Argument:
    reserved_names = []
    reserved_aliases = []
    
    @staticmethod
    def validate_name(v: str) -> bool:
        return v and re.match(r'[a-z][a-z\d_]+[a-z0-9]', v) is not None
    
    @staticmethod
    def validate_alias(v: str) -> bool:
        return v and re.match(r'[\-{1,2}][a-z][a-z\d-]+[a-z0-9]', v) is not None

    @property
    def name(self):
        return self._name
    
    @property
    def aliases(self):
        return self._aliases

    @property
    def mode(self):
        return self._mode

    @property
    def type(self):
        return self._type

    @property
    def omitted_value(self):
        return self._omitted_value

    @property
    def default_value(self):
        return self._default_value

    @property
    def hint(self):
        return self._hint
    
    def __init__(self,
                 name: str,
                 aliases: Optional[Iterable[str]] = None,
                 mode: ArgumentMode = DEFAULT_ARGUMENT_MODE,
                 type: Optional[Type] = None,
                 omitted_value: Optional[Any] = None,
                 default_value: Optional[Any] = None,
                 required: bool = False,
                 hint: Optional[str] = None,
                 value: Optional[bytes] = None):
        assert Argument.validate_name(name)
        assert name not in self.reserved_names
        self.reserved_names.append(name)
        
        for alias in aliases:
            assert Argument.validate_alias(alias)
            assert alias not in self.reserved_aliases
            self.reserved_aliases.append(alias)
        
        self._name = name
        self._aliases = set(aliases)
        self._mode = mode
        self._type = type
        self._omitted_value = omitted_value
        self._default_value = default_value
        self._required = required
        self._hint = hint
        
        self.value = value
    
    def as_text(self, encoding: str = 'utf-8', errors: str = 'strict') -> Optional[str]:
        if self.value:
            return self.value.decode(encoding, errors)
        return None
    
    def as_int(self, base: int = 10) -> Optional[int]:
        pass
    
    def as_float(self, rounding: int = -1) -> Optional[float]:
        pass
    
    def as_path(self) -> Optional[Path]:
        pass


class CLI:
    
    def __init__(self):
        self._arguments: List[Argument] = []
    
    def argument(self,
                 name: str,
                 aliases: Optional[Iterable[str]] = None,
                 mode: ArgumentMode = DEFAULT_ARGUMENT_MODE,
                 type: Optional[Type] = None,
                 omitted_value: Optional[Any] = None,
                 default_value: Optional[Any] = None,
                 required: bool = False,
                 hint: Optional[str] = None) -> Argument:
        pass
    
    def parse(self):
        pass
    
    def format_usage(self) -> str:
        pass
    
    def print_usage(self, fd: Optional[TextIO] = None):
        pass


# cli = CLI()
# input_file = cli.argument('input_file', '-i')
#
# try:
#     cli.parse()
# except InvalidUsage as e:
#     for unknown_arg in e.unknown_arguments:
#         print(f'- {unknown_arg.name}')
#
#     print(cli.format_usage())
#     exit(1)
# except Positioning as e:
#     pass
# except Ambiguity as e:
#     pass
