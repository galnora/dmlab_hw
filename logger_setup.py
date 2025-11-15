import logging
import os

def setup_logger(service_name: str):
    ### Global logger for every services
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger