# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

# aiofiles - Apache License 2.0
# Copyright (c) 2024, Tinche
# For more details, see the LICENSE file included with the distribution
from aiocache import cached, Cache


class TimeZoneConverter:

    # 設置起始時區為GMT，目標時區為臺北時間

    from_tz = ZoneInfo("GMT")
    to_tz = ZoneInfo("Asia/Taipei")

    @cached(ttl=600, cache=Cache.MEMORY)
    async def convert_time(
        self,
        time_str: str,
        format: str = "%a, %d %b %Y %H:%M:%S %Z",
        output_format: str = "%Y/%m/%d %H:%M:%S",
    ) -> str:

        # 異步方法，用於將時間從一個時區轉換到另一個時區並格式化輸出
        try:

            # 將時間字符串轉換為時間對象，並設置起始時區
            time_obj = datetime.strptime(
                time_str, format).replace(tzinfo=self.from_tz)

            # 將時間轉換到目標時區並按指定格式輸出
            return time_obj.astimezone(self.to_tz).strftime(output_format)
        except ValueError as e:
            raise ValueError(f"時間格式錯誤: {e}")


# 異步方法，用於獲取當前時間並按指定格式輸出
@ lru_cache(maxsize=1800)
async def get_formatted_current_time(
    format_string: str = "%Y/%m/%d %H:%M:%S"
) -> str:
    # 獲取當前時間並按指定格式輸出
    return datetime.now().strftime(format_string)
