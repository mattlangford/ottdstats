import logging
import datetime

__log_format = "ottdstats: %(timestamp)s: %(message)s"

def log_debug(message):
    logging.debug(__create_log_entry(message))

def log_error(message):
    logging.debug(__create_log_entry(message))

def log_info(message):
    logging.debug(__create_log_entry(message))

def log_warning(message):
    logging.debug(__create_log_entry(message))

def __create_log_entry(message):
    return __log_format.format({
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'message': message
    })

