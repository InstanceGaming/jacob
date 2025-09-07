import os
import re
import sys
import logging
import functools
from enum import IntEnum, IntFlag
from typing import Set, Tuple, Union, Optional
from pathlib import Path
from datetime import timedelta
from functools import partialmethod
from dataclasses import dataclass
from jacob.types import PathLike


QUENCH_LOG_EXCEPTIONS = True
LOG_LEVEL_PATTERN = re.compile(r'^([a-z_]+|[0-9]+)(,([a-z_]+|[0-9]+))?$', flags=re.IGNORECASE)
CUSTOM_LEVEL_NAME_PATTERN = re.compile(r'^[a-z_][a-z0-9_]+$', flags=re.IGNORECASE)


class LoggerConfigError(Exception):
    pass


class LoggingFileStructureError(LoggerConfigError):
    pass


class LoggingFacilityError(LoggerConfigError):
    pass


@dataclass(frozen=True, slots=True)
class SinkLevels:
    default: Tuple[int, int]
    stdout: Tuple[int, int]
    stderr: Tuple[int, int]
    file: Tuple[int, int]


@dataclass(frozen=True)
class CustomLevel:
    id: int
    name: str
    color_format: Optional[str] = None


class LogLevel(IntEnum):
    TRACE = 5
    VERBOSE = 8
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


LEVEL_COLOR_FORMATS = {
    LogLevel.TRACE   : '<w><d>',
    LogLevel.DEBUG   : '<e>',
    LogLevel.INFO    : '<lw>',
    LogLevel.SUCCESS : '<lg>',
    LogLevel.WARNING : '<ly>',
    LogLevel.ERROR   : '<lr><b>',
    LogLevel.CRITICAL: '<r><b><l>'
}


def _generate_levels():
    for level in LogLevel:
        color_format = None
        for k, v in reversed(LEVEL_COLOR_FORMATS.items()):
            if k <= level:
                color_format = v
                break
        yield CustomLevel(level.value, level.name, color_format=color_format)


DEFAULT_LEVELS = _generate_levels()
RECOMMENDED_LEVELS = (f'{LogLevel.INFO},{LogLevel.WARNING};'
                      f'stderr={LogLevel.ERROR},{LogLevel.CRITICAL};'
                      f'file={LogLevel.DEBUG},{LogLevel.CRITICAL}')
RECOMMENDED_LEVELS_DEBUG = (f'{LogLevel.DEBUG},{LogLevel.WARNING};'
                            f'stderr={LogLevel.ERROR},{LogLevel.CRITICAL};'
                            f'file={LogLevel.DEBUG},{LogLevel.CRITICAL}')
RECOMMENDED_LEVELS_ALL = (f'{LogLevel.TRACE},{LogLevel.WARNING};'
                          f'stderr={LogLevel.ERROR},{LogLevel.CRITICAL};'
                          f'file={LogLevel.TRACE},{LogLevel.CRITICAL}')


def parse_log_level_shorthand(l, spec: Optional[str]) -> SinkLevels:
    def _parse_range(sink, syntax) -> Tuple[int, int]:
        pattern_result = LOG_LEVEL_PATTERN.match(syntax)
        if pattern_result is not None:
            def coerce_level(_value: Union[int, str]) -> int:
                try:
                    return int(_value)
                except ValueError:
                    try:
                        _value = _value.upper()
                        return l.level(_value).no
                    except ValueError:
                        raise ValueError(f'unknown logging level "{_value}" for sink "{sink}"')
            
            lower = coerce_level(pattern_result.group(1))
            upper_text = pattern_result.group(3)
            
            upper: Optional[int] = None
            if upper_text is not None:
                upper = coerce_level(upper_text) + 1
                
                if lower > upper:
                    raise ValueError(f'impossible logging lower level range defined for sink '
                                     f'"{sink}" ({lower} > {upper})')
            
            return lower, upper
        else:
            raise ValueError(f'invalid logging level "{syntax}" for sink "{sink}"')
    
    levels = {
        'default': (0, sys.maxsize),
        'stdout' : None,
        'stderr' : None,
        'file'   : None
    }
    if spec:
        cleaned = spec.strip()
        default_defined = False
        for part in cleaned.split(';'):
            part = part.strip()
            if '=' in part:
                kv_parts = part.split('=')
                key = kv_parts[0]
                
                if key not in levels.keys():
                    raise KeyError(f'unknown logging sink "{key}"')
                
                levels[key] = _parse_range(key, kv_parts[1])
            else:
                if default_defined:
                    raise ValueError('default already defined')
                
                levels['default'] = _parse_range('default', part)
                default_defined = True
    
    for k, v in levels.items():
        if k != 'default':
            if v is None:
                levels[k] = levels['default']
    
    return SinkLevels(
        levels['default'],
        levels['stdout'],
        levels['stderr'],
        levels['file']
    )


class FormatContents(IntFlag):
    NONE = 0b00000000
    MESSAGE = 0b00000001
    LEVEL = 0b00000010
    FUNCTION = 0b00000100
    SOURCE = 0b00001000
    MODULE = 0b00010000
    THREAD = 0b00100000
    PROCESS = 0b01000000
    TIMESTAMP = 0b10000000


DEFAULT_FORMAT_CONTENTS = (FormatContents.LEVEL |
                           FormatContents.MESSAGE)
DEFAULT_FILE_FORMAT_CONTENTS = (FormatContents.TIMESTAMP |
                                FormatContents.PROCESS |
                                FormatContents.THREAD |
                                FormatContents.MODULE |
                                FormatContents.SOURCE |
                                FormatContents.FUNCTION |
                                FormatContents.LEVEL |
                                FormatContents.MESSAGE)


def default_filter_func(record, max_level: Optional[int] = None):
    return max_level is None or record['level'].no < max_level


def setup_sink(l,
               sink,
               levels: Tuple[int, Optional[int]],
               color=False,
               format_contents: FormatContents = DEFAULT_FORMAT_CONTENTS,
               rotation=None,
               retention=None,
               compression=None,
               mode='a',
               serialize=False,
               backtrace=False,
               diagnose=False,
               enqueue=False,
               context=None,
               filter_func=default_filter_func):
    fmt = ''
    
    if format_contents & FormatContents.TIMESTAMP:
        fmt += '<w>[{time:YYYY-MM-DD hh:mm:ss A}]</w>'
    
    if format_contents & FormatContents.PROCESS:
        fmt += '<w>[{process}]</w>'
    
    if format_contents & FormatContents.THREAD:
        fmt += '<w>[{thread}]</w>'
    
    if format_contents & FormatContents.MODULE:
        fmt += '<w>[{module}]</w>'
    
    if format_contents & FormatContents.SOURCE:
        fmt += '<w>[{file}:{line}]</w>'
    
    if format_contents & FormatContents.FUNCTION:
        fmt += '<w>[{function}]</w>'
    
    if fmt:
        fmt += ' '
    
    if format_contents & FormatContents.LEVEL:
        fmt += '<level>{level: >8}</level>'
    
    if fmt:
        fmt += ': '
    
    if format_contents & FormatContents.MESSAGE:
        fmt += '{message} '
    
    kwargs = {
        'colorize' : color,
        'level'    : levels[0],
        'format'   : fmt,
        'serialize': serialize,
        'backtrace': backtrace,
        'diagnose' : diagnose,
        'catch'    : QUENCH_LOG_EXCEPTIONS,
        'enqueue'  : enqueue,
        'context'  : context
    }
    
    max_level = levels[1]
    kwargs.update({
        'filter': functools.partial(filter_func, max_level=max_level),
    })
    
    if isinstance(sink, (str, Path)):
        sink = str(sink)
        
        kwargs.update({
            'rotation'   : rotation,
            'retention'  : retention,
            'compression': compression,
            'mode'       : mode
        })
    
    l.add(sink, **kwargs)
    return l


def setup_logger(log_levels: Union[SinkLevels, str],
                 custom_levels: Optional[Set[CustomLevel]] = DEFAULT_LEVELS,
                 log_file: Optional[PathLike] = None,
                 rotation: timedelta = timedelta(days=1),
                 retention: timedelta = timedelta(days=7),
                 standard_json=False,
                 color=True,
                 format_contents=DEFAULT_FORMAT_CONTENTS,
                 file_format_contents=None,
                 file_json=False,
                 file_mode='a',
                 file_compression='gz',
                 backtrace=True,
                 diagnose=False,
                 enqueue=False,
                 context=None,
                 filter_func=default_filter_func,
                 file_filter_func=None):
    try:
        import loguru as _loguru_module
        bootstrap_logger = _loguru_module.logger
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError('the "loguru" module failed to import; this '
                                  'is required to use the logging features of '
                                  'jacobs library.') from e
    
    bootstrap_logger.remove()
    
    if custom_levels:
        """
        Hack for loguru version 0.7.3 to allow for re-defining the default log
        level names. This worked in version 0.7.2 by just calling level() again.
        If you know of a better way to do this, I'm all ears, but I don't want to
        use different level names while still being free to use my own integer
        scale.
        """
        logger_core = getattr(bootstrap_logger, '_core')
        logger_core.levels.clear()
        
        klass = bootstrap_logger.__class__
        for custom_level in custom_levels:
            assert CUSTOM_LEVEL_NAME_PATTERN.match(custom_level.name)
            try:
                bootstrap_logger.level(custom_level.name, no=custom_level.id, color=custom_level.color_format)
            except TypeError:
                continue
            setattr(klass, custom_level.name.lower(), partialmethod(klass.log, custom_level.name))
    
    if isinstance(log_levels, str):
        log_levels = parse_log_level_shorthand(bootstrap_logger, log_levels)
    elif isinstance(log_levels, SinkLevels):
        log_levels = log_levels
    else:
        raise TypeError('log_levels must be a str or SinkLevels instance')
    
    try:
        logger = setup_sink(bootstrap_logger,
                            sys.stdout,
                            log_levels.stdout,
                            color=color,
                            format_contents=format_contents,
                            serialize=standard_json,
                            enqueue=enqueue,
                            context=context,
                            filter_func=filter_func)
        
        logger = setup_sink(logger,
                            sys.stderr,
                            log_levels.stderr,
                            color=color,
                            format_contents=format_contents,
                            backtrace=backtrace,
                            diagnose=diagnose,
                            enqueue=enqueue,
                            context=context,
                            filter_func=filter_func)
        
        if log_file is not None:
            log_file = Path(log_file)
            try:
                os.makedirs(log_file.absolute().parent, exist_ok=True)
            except OSError as e:
                raise LoggingFileStructureError from e
            
            logger = setup_sink(
                logger,
                log_file,
                log_levels.file,
                format_contents=file_format_contents or format_contents or DEFAULT_FILE_FORMAT_CONTENTS,
                rotation=rotation,
                retention=retention,
                compression=file_compression,
                mode=file_mode,
                serialize=file_json,
                backtrace=backtrace,
                diagnose=diagnose,
                enqueue=enqueue,
                context=context,
                filter_func=file_filter_func or filter_func
            )
    
    except (ValueError, TypeError) as e:
        raise LoggingFacilityError from e
    
    return logger


def attach_standard_logger(loguru_logger,
                           logger_name: str,
                           minimum_level: int = logging.DEBUG,
                           clear_handlers: bool = True):
    class Handler(logging.Handler):
        
        def emit(self, record: logging.LogRecord):
            _logger = loguru_logger.bind()
            level = record.levelname
            _logger.log(level, record.getMessage())
    
    standard_logger = logging.getLogger(logger_name)
    standard_logger.setLevel(minimum_level)
    
    if clear_handlers:
        for handler in standard_logger.handlers:
            standard_logger.removeHandler(handler)
    
    standard_logger.addHandler(Handler())
