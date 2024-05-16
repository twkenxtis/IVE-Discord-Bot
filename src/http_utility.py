import aiohttp
import logging
from datetime import datetime

from fake_useragent import UserAgent
from timezone import SystemTime
from custom_log import ColoredLogHandler

logging.basicConfig(level=logging.INFO, handlers=[ColoredLogHandler()])


class HttpRequester:

    def __init__(self, url):
        self.url = url
        self.response_content = None

    async def send_request(self):
        ua = UserAgent()
        headers = {"user-agent": ua.random}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers, timeout=10) as response:
                self.response_content = await response.text()
                return response.status

    async def get_response_content(self):
        return str(self.response_content)

    async def start_requests(self):
        status_code = await self.send_request()
        current_time = SystemTime.format_current_time()
        if status_code == 200:
            print(
                f"\033[38;2;102;153;153mSystem current time: {current_time}\033[0m")
            logging.info(f" {self.url} code: {status_code}")
        else:
            print(
                f"\033[38;2;102;153;153mSystem current time: {current_time}\033[0m")
            logging.warning(f" {self.url} code: {status_code}")
