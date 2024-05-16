import logging

from timezone import get_formatted_current_time
from custom_log import ColoredLogHandler

import aiohttp
from aiohttp import ClientTimeout
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO, handlers=[ColoredLogHandler()])


class HttpRequester:

    def __init__(self, url):
        self.url = url
        self.response_content = None
        self.status_message = "失敗，無法連線"
        self.headers = {"user-agent": UserAgent().random}
        self.session = aiohttp.ClientSession()

    async def send_request(self):
        timeout = ClientTimeout(total=20)
        try:
            async with self.session.get(self.url, headers=self.headers, timeout=timeout) as response:
                self.response_content = await response.text()
                self.status_message = f"HTTP Status Code: {response.status}"
                return response.status
        except aiohttp.ClientError as e:
            logging.error(f" {await get_formatted_current_time()} - ClientError: {e} - 網路請求錯誤")
            return "失敗，網路請求錯誤"

    async def get_response_content(self):
        return str(self.response_content)

    async def start_requests(self):
        status_code_or_message = await self.send_request()
        if status_code_or_message == 200:
            logging.info(f" {await get_formatted_current_time()} - {self.url} code: {status_code_or_message}")
        else:
            logging.warning(f" {await get_formatted_current_time()} - {self.url} - {status_code_or_message}")

    async def close(self):
        await self.session.close()
