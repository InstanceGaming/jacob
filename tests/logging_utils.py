from jacob.logging import (
    RECOMMENDED_LEVELS,
    RECOMMENDED_LEVELS_ALL,
    LogLevel,
    FormatContents
)


def test_setup_sink():
    from loguru import logger as loguru_logger
    from jacob.logging import setup_logger, parse_log_level_shorthand
    result = parse_log_level_shorthand(loguru_logger, RECOMMENDED_LEVELS)
    logger = setup_logger(result, log_file='test.log')
    logger.trace('abc')
    logger.info('def')
    logger.error('ghi')
    logger.critical('jkl')
    assert result['stdout'] == (10, 31)
    assert result['stderr'] == (40, 51)
    assert result['file'] == (20, 51)


def test_setup_logger():
    from jacob.logging import setup_logger
    
    contents = (FormatContents.TIMESTAMP |
                FormatContents.SOURCE |
                FormatContents.LEVEL |
                FormatContents.MESSAGE)
    logger = setup_logger(RECOMMENDED_LEVELS_ALL,
                          format_contents=contents,
                          log_file='data/test.txt')
    for level in LogLevel:
        func = getattr(logger, level.name.lower())
        func('test of level {}', level.name)
    
    with logger.catch():
        raise ValueError('uh oh')


test_setup_logger()
