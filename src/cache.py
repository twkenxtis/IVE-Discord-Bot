# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import aiofiles
import asyncio
import json
import os
import pickle

import nest_asyncio
# nest_asyncio - BSD 2-Clause License
# Copyright (c) 2018-2020, Ewald de Wit
# For more details, see the LICENSE file included with the distribution
from loguru import logger
# loguru is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution


class CacheManager:
    def __init__(self):
        # 初始化緩存管理器，設置緩存字典和文件路徑
        self.pkl_cache = {}
        self.json_cache = {}
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path_pkl = os.path.join(
            self.script_dir, '..', 'assets', 'Twitter_dict.pkl'
        )
        self.file_path_json = os.path.join(
            self.script_dir, '..', 'assets', 'Twitter_dict.json'
        )
        self.loop = asyncio.get_event_loop()
        # 允許 nest_asyncio 嵌套的事件循環
        nest_asyncio.apply(self.loop)
        self.pkl_len = None
        self.json_len = None

    async def load_cache(self):
        re_try = 0
        while True:
            if os.path.exists(self.file_path_pkl):
                async with aiofiles.open(self.file_path_pkl, 'rb') as pkl_file:
                    try:
                        content = await pkl_file.read()
                        self.pkl_cache = pickle.loads(content)
                        break
                    except EOFError:
                        await asyncio.sleep(0.05)
                    except Exception:
                        await asyncio.sleep(0.05)
            else:
                re_try + 1
                print("Error: 找不到 Twitter_dict.pkl 文件，重試中...")
                await asyncio.sleep(1)
                if re_try == 10:
                    break

        if os.path.exists(self.file_path_json):
            try:
                async with aiofiles.open(self.file_path_json, 'r') as json_file:
                    self.json_cache = json.loads(await json_file.read())
            except json.JSONDecodeError:
                async with aiofiles.open(self.file_path_json, 'w') as json_file:
                    await json_file.write(json.dumps({}))
                    pass
        else:
            logger.error(
                f"Twitter_dict.pkl not found: {self.file_path_pkl}\n OR Twitter_dict.json not found: {self.file_path_json}"
            )
            raise FileNotFoundError("OOPS ! File not found! Can't start!")

    async def save_cache(self):
        # 異步存入緩存數據
        async with aiofiles.open(self.file_path_pkl, 'wb') as pkl_file:
            await pkl_file.write(pickle.dumps(self.pkl_cache))

        # 因為美觀關係格式化 json 因此不使用 orjson
        async with aiofiles.open(self.file_path_json, 'w') as json_file:
            await json_file.write(json.dumps(self.json_cache, indent=4))

    # 異步更新緩存數據
    async def dc_cache_async(self, MD5):

        # 硬編碼的固定值，表示該訊息已經在Discord傳送成功
        value = 'SENDED'

        if MD5 not in self.pkl_cache:
            self.pkl_cache[MD5] = []
        else:
            self.pkl_cache[MD5] = list(self.pkl_cache[MD5])  # 將原始資料型態元組轉換為列表

        if MD5 not in self.json_cache:
            self.json_cache[MD5] = []

        self.pkl_len = len(self.pkl_cache[MD5])
        self.json_len = len(self.json_cache[MD5])
        if self.pkl_len and self.json_len == 9:
            self.pkl_cache[MD5].append(value)
            self.json_cache[MD5].append(value)
            await self.save_cache()
        else:
            await asyncio.sleep(0.05)
            cache_manager.initialize_cache()

    # MD5 是字典中固定的Key 接收外部傳入的MD5值

    def dc_cache(self, MD5):
        # 使用事件循環運行異步任務
        self.loop.run_until_complete(self.dc_cache_async(MD5))

    def initialize_cache(self):
        # 初始化緩存
        self.loop.run_until_complete(self.load_cache())


cache_manager = CacheManager()
cache_manager.initialize_cache()
