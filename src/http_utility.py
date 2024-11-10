# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import logging

# aiocache - BSD 3-Clause License
# Copyright (c) 2016, Manuel Miranda de Cid
# For more details, see the LICENSE file included with the distribution
import asyncio
import aiohttp
from aiohttp import ClientTimeout
# fake-useragent - Apache License 2.0
# Copyright (c) 2024, fake-useragent
# For more details, see the LICENSE file included with the distribution
from fake_useragent import UserAgent
# orjson is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution
from loguru import logger

logging.basicConfig(level=logging.INFO)


class HttpRequester:
    def __init__(self, url, max_retries=3, retry_delay=5):
        self.url = url
        self.response_content = None
        self.status_message = "失敗，無法連線"
        self.headers = {"user-agent": UserAgent().random}
        self.session = aiohttp.ClientSession()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def send_request(self):
        timeout = ClientTimeout(total=20)
        retries = 0

        while retries < self.max_retries:
            try:
                async with self.session.get(self.url, headers=self.headers, timeout=timeout) as response:
                    self.response_content = await response.text()
                    self.status_message = f"HTTP Status Code: {response.status}"
                    return response.status
            except asyncio.TimeoutError:
                logger.warning(
                    f"TimeoutError: Request timed out for {self.url}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
                retries += 1
            except aiohttp.ClientError as e:
                logger.error(f"ClientError: {e} - 網路請求錯誤")
                return "失敗，網路請求錯誤"

        # Close session if max retries exceeded
        await self.close()
        return "失敗，超過最大重試次數"

    async def get_response_content(self):
        return str(self.response_content)

    async def start_requests(self):
        status_code_or_message = await self.send_request()
        if status_code_or_message == 200:
            logger.info(f"{self.url} ─ {status_code_or_message}")
        else:
            logger.warning(f"{self.url} ─ {status_code_or_message}")

    async def close(self):
        await self.session.close()
