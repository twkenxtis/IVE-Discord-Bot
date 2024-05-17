import os

from loguru import logger


logger_API_Twitter = logger.opt(depth=1, lazy=True)
logger_API_Twitter_path = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'logs', 'twitter')
logger_API_Twitter.add(f'{logger_API_Twitter_path}/'"{time}.log",
                       level="WARNING", encoding="utf-8", enqueue=True, rotation="20 MB")
