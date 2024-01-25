import os
import re
import sys
from dataclasses import dataclass
from datetime import timedelta
from functools import partialmethod
from pathlib import Path
from typing import Optional, TypedDict, Union, Tuple, Set
from jacob.types import PathLike


QUENCH_LOG_EXCEPTIONS = True
RECOMMENDED_LEVELS = 'DEBUG,WARNING;stderr=ERROR,CRITICAL;file=INFO,CRITICAL'
LOG_LEVEL_PATTERN = re.compile(r'^([a-z_]+|\d+)(,([a-z_]+|\d+))?$', flags=re.IGNORECASE)
CUSTOM_LEVEL_NAME_PATTERN = re.compile(r'^[a-z_][a-z0-9_]+$', flags=re.IGNORECASE)


class LoggerConfigError(Exception):
    pass


class LoggingFileStructureError(LoggerConfigError):
    pass


class LoggingFacilityError(LoggerConfigError):
    pass


class SinkLevels(TypedDict):
    default: Tuple[int, int]
    stdout: Tuple[int, int]
    stderr: Tuple[int, int]
    file: Tuple[int, int]


@dataclass(frozen=True)
class CustomLevel:
    id: int
    name: str
    color_code: Optional[str] = None


def parse_log_level_shorthand(l, spec: Optional[str]) -> SinkLevels:
    def _parse_range(sink, syntax) -> tuple:
        pattern_result = LOG_LEVEL_PATTERN.match(syntax)
        if pattern_result is not None:
            def coerce_level(_value: Union[int, str]) -> int:
                try:
                    return int(_value)
                except ValueError:
                    try:
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
    
    default_level = levels.pop('default')
    for k, v in levels.items():
        if v is None:
            levels[k] = default_level
    
    return levels


def setup_sink(l,
               sink,
               levels: Tuple[int, Optional[int]],
               color=False,
               timestamp=False,
               rotation=None,
               retention=None,
               compression=None,
               mode='a',
               serialize=False,
               backtrace=False,
               diagnose=False,
               enqueue=False,
               context=None):
    fmt = '<level>{level: >8}</level>: {message} '
    if timestamp:
        fmt = '[{time:YYYY-MM-DD hh:mm:ss A}] ' + fmt
    if __debug__:
        fmt += '<d>[<i>{file}:{line}</i>]</d> '
    
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
    if max_level is not None:
        kwargs.update({'filter': lambda record: record['level'].no < max_level})
    
    if isinstance(sink, str):
        kwargs.update({
            'rotation'   : rotation,
            'retention'  : retention,
            'compression': compression,
            'mode'       : mode
        })
    
    l.add(sink, **kwargs)
    return l


def setup_logger(log_levels: Union[SinkLevels, str],
                 custom_levels: Optional[Set[CustomLevel]] = None,
                 log_file: Optional[PathLike] = None,
                 rotation: timedelta = timedelta(days=1),
                 retention: timedelta = timedelta(days=7),
                 standard_json=False,
                 file_json=False,
                 backtrace=True,
                 diagnose=False,
                 enqueue=False,
                 context=None):
    try:
        import loguru as _loguru_module
        
        bootstrap_logger = _loguru_module.logger
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError('the "loguru" module failed to import; this '
                                  'is required to use the logging features of '
                                  'jacobs library.') from e
    
    bootstrap_logger.remove()
    
    if custom_levels:
        klass = bootstrap_logger.__class__
        for custom_level in custom_levels:
            assert CUSTOM_LEVEL_NAME_PATTERN.match(custom_level.name)
            color_format = f'<{custom_level.color_code}>' if custom_level.color_code else None
            bootstrap_logger.level(custom_level.name, no=custom_level.id, color=color_format)
            setattr(klass, custom_level.name, partialmethod(klass.log, custom_level.name))
    
    if isinstance(log_levels, str):
        log_levels = parse_log_level_shorthand(bootstrap_logger, log_levels)
    
    stdout_level = log_levels['stdout']
    stderr_level = log_levels['stderr']
    
    try:
        logger = setup_sink(bootstrap_logger,
                            sys.stdout,
                            stdout_level,
                            color=True,
                            serialize=standard_json,
                            enqueue=enqueue,
                            context=context)
        
        logger = setup_sink(logger,
                            sys.stderr,
                            stderr_level,
                            color=True,
                            backtrace=backtrace,
                            diagnose=diagnose,
                            enqueue=enqueue,
                            context=context)
        
        if log_file is not None:
            file_level = log_levels['file']
            log_file = Path(log_file)
            try:
                os.makedirs(log_file.absolute().parent, exist_ok=True)
            except OSError as e:
                raise LoggingFileStructureError from e
            
            logger = setup_sink(logger,
                                log_file,
                                file_level,
                                timestamp=True,
                                rotation=rotation,
                                retention=retention,
                                compression='gz',
                                serialize=file_json,
                                backtrace=backtrace,
                                diagnose=diagnose,
                                enqueue=enqueue)
    
    except (ValueError, TypeError) as e:
        raise LoggingFacilityError from e
    
    return logger
