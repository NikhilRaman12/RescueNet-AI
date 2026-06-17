import logging


def configure_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger('rescuenet')
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    return logger


logger = configure_logging()
