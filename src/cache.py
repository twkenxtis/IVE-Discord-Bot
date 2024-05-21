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
            self.script_dir, '..', 'assets', 'Twitter_dict.pkl')
        self.file_path_json = os.path.join(
            self.script_dir, '..', 'assets', 'Twitter_dict.json')
        self.loop = asyncio.get_event_loop()
       # 允許 nest_asyncio 嵌套的事件循環
        nest_asyncio.apply(self.loop)

    async def load_cache(self):
        # 異步載入緩存數據
        if os.path.exists(self.file_path_pkl):
            async with aiofiles.open(self.file_path_pkl, 'rb') as pkl_file:
                self.pkl_cache = pickle.loads(await pkl_file.read())

        if os.path.exists(self.file_path_json):
            async with aiofiles.open(self.file_path_json, 'r') as json_file:
                self.json_cache = json.loads(await json_file.read())
        else:
            # TODO: 之後再想資料庫如果被刪除怎麼處理
            logger.error(
                f"Twitter_dict.pkl not found: {self.file_path_pkl} 或 Twitter_dict.json not found: {self.file_path_json}")

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

        self.pkl_cache[MD5].append(value)
        self.json_cache[MD5].append(value)

        await self.save_cache()

    # MD5 是字典中固定的Key 接收外部傳入的MD5值
    def dc_cache(self, MD5):
        # 使用事件循環運行異步任務
        self.loop.run_until_complete(self.dc_cache_async(MD5))

    def initialize_cache(self):
        # 初始化緩存
        self.loop.run_until_complete(self.load_cache())


cache_manager = CacheManager()
cache_manager.initialize_cache()
