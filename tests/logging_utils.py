from typing import Optional
from jacob.logging import (
    RECOMMENDED_LEVELS,
    RECOMMENDED_LEVELS_ALL,
    LogLevel,
    FormatContents
)


def category_filter_factory(wanted_category):
    def filter_func(record, max_level: Optional[int] = None):
        if record['extra'].get('category') != wanted_category:
            return False
        return max_level is None or record['level'].no < max_level
    return filter_func


def test_setup_sink():
    from loguru import logger as loguru_logger
    from jacob.logging import setup_logger, parse_log_level_shorthand
    
    result = parse_log_level_shorthand(loguru_logger, RECOMMENDED_LEVELS)
    assert result.stdout == (20, 31)
    assert result.stderr == (40, 51)
    assert result.file == (10, 51)
    logger1 = setup_logger(result, log_file='data/test.log')
    logger2 = logger1.bind(category='cat1')
    logger1.trace('abc')
    logger1.info('def')
    logger1.error('ghi')
    logger1.critical('jkl')
    logger2.trace('abc (cat1)')
    logger2.info('def (cat1)')
    logger2.error('ghi (cat1)')
    logger2.critical('jkl (cat1)')


def test_setup_logger():
    from jacob.logging import setup_logger
    
    contents = (FormatContents.TIMESTAMP |
                FormatContents.SOURCE |
                FormatContents.LEVEL |
                FormatContents.MESSAGE)
    logger1 = setup_logger(RECOMMENDED_LEVELS_ALL,
                           format_contents=contents,
                           log_file='data/test.log',
                           diagnose=True)
    logger2 = logger1.bind(category='cat1')
    
    for level in LogLevel:
        func = getattr(logger1, level.name.lower())
        func('test of level {}', level.name)
        func = getattr(logger2, level.name.lower())
        func('test of level {} (cat1)', level.name)
    
    with logger1.catch():
        raise ValueError('uh oh')
    with logger2.catch():
        raise ValueError('uh oh (cat1)')

test_setup_sink()
test_setup_logger()