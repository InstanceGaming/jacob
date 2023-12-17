from jacob.logging import RECOMMENDED_LEVELS


def test_parser_all():
    from loguru import logger as loguru_logger
    from jacob.logging import parse_log_level_shorthand, setup_logger
    result = parse_log_level_shorthand(loguru_logger, RECOMMENDED_LEVELS)
    logger = setup_logger(result, log_file='test.log')
    logger.trace('abc')
    logger.info('def')
    logger.error('ghi')
    logger.critical('jkl')
    assert result['stdout'] == (10, 21)
    assert result['stderr'] == (40, None)
    assert result['file'] == (20, 51)
