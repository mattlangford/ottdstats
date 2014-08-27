import logging
import datetime

__log_format = "{timestamp} {message}"
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('ottdstats')

def log_debug(message):
    logger.debug(__create_log_entry(message))

def log_error(message):
    logger.error(__create_log_entry(message), exc_info=True)

def log_info(message):
    logger.info(__create_log_entry(message))

def log_warning(message):
    logger.warning(__create_log_entry(message))

def __create_log_entry(message):
    return __log_format.format(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        message=message)

