import os
import logging

def setup_logger(name="rag_pipeline"):
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Wrap logger.log to respect env level
    def smart_log(message):
        logger.log(level, message)

    logger.smart_log = smart_log
    return logger