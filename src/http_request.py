import logging
import random
import asyncio
from datetime import datetime

import httpx
from fake_useragent import UserAgent

from src.timezone import SystemTime
from src.custom_log import ColoredLogHandler


class HTTP3Requester:
    def __init__(self, url):
        logging.basicConfig(level=logging.INFO, handlers=[ColoredLogHandler()])
        self.url = url
        self.response_content = None

    async def send_request(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, timeout=5)
            self.response_content = response.text

    def get_response_content(self):
        return self.response_content

    async def make_request(self):
        ua = UserAgent()
        headers = {"user-agent": ua.random}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.url, headers=headers, timeout=10)
                if response is not None and 200 == response.status_code:
                    self.response_content = response.text
                    logging.info(
                        f"System current time : {SystemTime.format_current_time()}"
                    )
                else:
                    logging.warning(
                        f"System current time : {SystemTime.format_current_time()}"
                        f" HTTP response code : {response.status_code}"
                    )
            except Exception as HTTP_ERROR_EXCEPTION:
                logging.error(
                    f"System current time: {SystemTime.format_current_time()}"
                    f" Error: {str(HTTP_ERROR_EXCEPTION)}"
                )
            return self.response_content

    async def start_requests(self, num_of_requests):
        if num_of_requests > 1:
            print(
                f"\033[91m Requests: \033[0m\033[38;5;118m{num_of_requests}\033[0m \033[38;2;255;212;128m > 1 Enable waiting time...\033[0m"
            )
            for _ in range(num_of_requests):
                sleep_time = random.randint(13, 29)
                await asyncio.sleep(sleep_time)
                await self.make_request()
                print(
                    f"\033[90m{SystemTime.format_current_time()}\033[0m "
                    f"\033[91m Waiting \033[0m \033[38;5;208m{sleep_time}s\033[0m \033[38;2;255;212;128m for request...\033[0m"
                )
        else:
            await self.make_request()
