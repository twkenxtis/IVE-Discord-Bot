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
        self.status_message = "失敗，無法連線"

    async def send_request(self):
        ua = UserAgent()
        headers = {"user-agent": ua.random}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, headers=headers, timeout=20) as response:
                    self.response_content = await response.text()
                    self.status_message = f"HTTP Status Code: {response.status}"
                    return response.status
        except aiohttp.client_exceptions.ClientOSError as e:
            logging.error(f"ClientOSError: {e} - 指定的網路名稱無法使用")
            return "失敗，無法連線"
        except TimeoutError as e:
            logging.error(f"TimeoutError: {e} - 指定的網路名稱無法連線")
            return "失敗，Timed out"

    async def get_response_content(self):
        return str(self.response_content)

    async def start_requests(self):
        status_code_or_message = await self.send_request()
        current_time = SystemTime.format_current_time()
        if status_code_or_message == 200:
            print(
                f"\033[38;2;102;153;153mSystem current time: {current_time}\033[0m")
            logging.info(f" {self.url} code: {status_code_or_message}")
        else:
            print(
                f"\033[38;2;102;153;153mSystem current time: {current_time}\033[0m")
            if isinstance(status_code_or_message, int):
                logging.warning(f" {self.url} code: {status_code_or_message}")
            else:
                logging.warning(f" {self.url} - {status_code_or_message}")
