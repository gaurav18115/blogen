import os
import logging
import logging.handlers

from logging.handlers import TimedRotatingFileHandler


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger(filename='theblogsystem.log'):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler with a different formatter (not JSON)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    color_formatter = CustomFormatter()
    ch.setFormatter(color_formatter)

    # Create rotating file handler
    subdirectory = '_logs'
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)
    filepath = os.path.join(subdirectory, filename)

    fh = TimedRotatingFileHandler(filepath, when='D', interval=1, backupCount=30)
    fh.setLevel(logging.INFO)

    # FIX: Use JsonFormatter for 3rd Party Tools
    # jfh = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    # jfh.setFormatter(file_formatter)

    fh.setFormatter(color_formatter)

    # Add the handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)


def construct_log_message(message, *args, **kwargs):
    log_message = message
    if args:
        log_message += f" - {args}"
    if kwargs:
        log_message += f" - {kwargs}"
    return log_message


def log_error(message, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.error(construct_log_message(message, *args, **kwargs))


def log_info(message, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info(construct_log_message(message, *args, **kwargs))


def log_debug(message, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.debug(construct_log_message(message, *args, **kwargs))

def log_warn(message, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.warn(construct_log_message(message, *args, **kwargs))
