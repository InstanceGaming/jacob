from jacob.logging import RECOMMENDED_LEVELS


def test_setup_sink():
    from loguru import logger as loguru_logger
    from jacob.logging import parse_log_level_shorthand, setup_logger
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
    
    logger = setup_logger('0,WARNING;stderr=ERROR,CRITICAL')
    logger.trace('abc')
    logger.info('def')
    logger.error('ghi')
    logger.critical('jkl')

test_setup_logger()
