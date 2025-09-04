import logging

logger = logging.getLogger("ai_marketplace")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def log_event(message: str):
    logger.info(message)