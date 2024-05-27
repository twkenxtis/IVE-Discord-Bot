# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import os

# orjson is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution
from loguru import logger


logger_API_Twitter = logger.opt(depth=1, lazy=True)
logger_API_Twitter_path = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'logs', 'twitter')
logger_API_Twitter.add(f'{logger_API_Twitter_path}/'"{time}.log",
                       level="error", encoding="utf-8", enqueue=True, rotation="1 MB")

logger_API__Discord = logger.opt(depth=1, lazy=True)
logger_API__Discord_path = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'logs', 'discord')
logger_API__Discord.add(f'{logger_API__Discord_path}/'"{time}.log",
                        level="error", encoding="utf-8", enqueue=True, rotation="1 MB")

logger_API__Main = logger.opt(depth=1, lazy=True)
logger_API__Main_path = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'logs')
logger_API__Main.add(f'{logger_API__Main_path}/'"{time}.log",
                     level="error", encoding="utf-8", enqueue=True, rotation="1 MB")
