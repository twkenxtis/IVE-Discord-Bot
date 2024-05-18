# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import logging

# aiocache - BSD 3-Clause License
# Copyright (c) 2016, Manuel Miranda de Cid
# For more details, see the LICENSE file included with the distribution
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

    def __init__(self, url):
        self.url = url
        self.response_content = None
        self.status_message = "失敗，無法連線"  # 默認狀態消息為“失敗，無法連接”
        self.headers = {"user-agent": UserAgent().random}  # 隨機生成User-Agent
        self.session = aiohttp.ClientSession()  # 創建Aiohttp客戶端會話

    async def send_request(self):
        timeout = ClientTimeout(total=20)  # 設置超時時間為20秒
        try:
            async with self.session.get(self.url, headers=self.headers, timeout=timeout) as response:
                self.response_content = await response.text()  # 獲取響應內容
                self.status_message = f"HTTP Status Code: {response.status}"
                return response.status
        except aiohttp.ClientError as e:
            logger.error(f"ClientError: {e} - 網路請求錯誤")
            return "失敗，網路請求錯誤"

    async def get_response_content(self):
        # 獲取響應內容並轉換為字符串
        return str(self.response_content)

    async def start_requests(self):
        status_code_or_message = await self.send_request()  # 發送網路請求
        if status_code_or_message == 200:
            logger.info(f"{self.url} ─ {status_code_or_message}")
            return
        else:
            logger.warning(f"{self.url} ─ {status_code_or_message}")
            return

    async def close(self):
        await self.session.close()  # 關閉會話
