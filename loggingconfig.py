from loguru import logger


def log_file():
    logger.add("file_{time}.log", format="{time} | {level} | {message}", level="INFO", encoding='utf-8')
    logger.debug("Debag message")