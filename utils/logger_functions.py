import logging
from logging.handlers import RotatingFileHandler

class IgnoreAutoreloadFile(logging.Filter):
    def filter(self, record):
        return "autoreload" not in record.getMessage()

# Convert log level strings to uppercase and validate them
def get_log_level(level):
    level = level.upper().strip()
    return getattr(logging, level, logging.DEBUG)