# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import asyncio
import hashlib
import json
import logging
import os
import re
import pickle
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import lru_cache
from typing import Tuple, Any, Dict, List, AsyncGenerator, Iterable, Optional, Type, Union
from xml.etree.ElementTree import Element
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from custom_log import logger_API_Twitter
from http_utility import HttpRequester
from ive_hash_tag import match_tags
from timezone import TimeZoneConverter, get_formatted_current_time

from aiocache import cached, Cache
# aiofiles - Apache License 2.0
# Copyright (c) 2024, Tinche
# For more details, see the LICENSE file included with the distribution
import aiofiles
# aiocache - BSD 3-Clause License
# Copyright (c) 2016, Manuel Miranda de Cid
# For more details, see the LICENSE file included with the distribution
import feedparser
# feedparser includes software developed by Kurt McKee (contactme@kurtmckee.org)
# and Mark Pilgrim (Copyright 2002-2008).
# For full license terms, see the LICENSE file included with this distribution.
from loguru import logger
# loguru is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution
import orjson
# orjson is used under the MIT License
# Copyright (c) 2024 ijl
# For more details, see the LICENSE file included with the distribution

logging.basicConfig(level=logging.INFO)


class TwitterHandler(object):

    # Default is False
    Dev_24hr_switch = False  # 開啟/關閉 24 小時開發模式

    # Default is True
    markdown_urls_switch = True  # 開啟/關閉 轉換 URL 為 Markdown 格式 (For Discord bot)
    if markdown_urls_switch is True:
        logger.info("Discord markdown url 模式已經開啟，將轉換所有 URL 為 Markdown 格式")
        pass

    PATTERN_tweet_img = re.compile(
        r'https://pbs.twimg.com/media/[^"\']+?\?format=jpg')
    PATTERN_video_thumb = re.compile(
        r'https://pbs.twimg.com/tweet_video_thumb/[^"\']+?\.(?:jpg)')
    PATTERN_mp4 = re.compile(r'https://video.twimg.com/[^"\']+?\.(?:mp4)')
    DESCRIPTION_PATTERN_TAG = re.compile(
        r'((?:.|\n)*?)(?:<img src="|<video controls="|<video src=")'
    )
    DESCRIPTION_PATTERN_AUTHOR = re.compile(
        r"https://pbs.twimg.com/profile_images/.+\.jpg$"
    )
    PATTERN_HASHTAG = re.compile(r"#(IVE|ive)", re.IGNORECASE)

    def __init__(self, url: str) -> None:
        self.url = url  # 初始化時傳入的 URL
        self.http_response_content: str | None = None  # 儲存 HTTP 回應內容
        self.parsed_rssfeed: feedparser.FeedParserDict | None = None  # 儲存解析後的 RSS Feed
        self.filter_entry = None  # 儲存過濾後的 Tweet 描述內容(標題/照片為主)
        self.rss_entry = None  # 儲存 RSS 條目
        self.description = None  # 儲存 RSS 條目的描述內容
        self.pub_date_tw = None  # RSS 條目的發布時間，由GMT轉換成台灣時區並且自訂為字串格式
        self.author_avatar = None  # 儲存作者頭像

    async def validate_url_and_get_feed(self) -> str:
        result = urlparse(self.url)
        if not all([result.scheme, result.netloc]):
            raise ValueError  # 捕捉在 start_API_Twitter.try_url

        await self.start_request()

    async def start_request(self) -> str:
        http_requester = HttpRequester(self.url)
        # 發送 HTTP 請求並取得回應內容
        await http_requester.start_requests()
        # 取得 HTTP 回應內容
        self.http_response_content = await http_requester.get_response_content()
        # 關閉 HTTP 請求器
        await http_requester.close()
        return self.http_response_content

    async def response_content(self) -> feedparser.FeedParserDict:
        # 取得並處理 RSS Feed 內容
        if self.http_response_content is not None:
            self.parsed_rssfeed = await self.parse_feed()
            async for self.parsed_rssfeed, self.pub_date_tw, self.description in self.main_feedparser(self.parsed_rssfeed):
                await self.process_entry(self.parsed_rssfeed)
            return self.parsed_rssfeed

    async def parse_feed(self) -> feedparser.FeedParserDict:
        # 使用 asyncio 獲取當前運行的 loop
        # 在執行器中非同步執行 feedparser.parse 方法
        return await asyncio.get_running_loop().run_in_executor(
            None, feedparser.parse, self.http_response_content
        )

    async def main_feedparser(
        self, tasks: List[asyncio.Task] = [], results: List[Tuple[Any, str, str]] = []
    ) -> AsyncGenerator[Tuple[Any, str, str], None]:
        if self.parsed_rssfeed is not None:
            # 收集所有符合條目的 tasks
            tasks = [
                self._process_rss_entry(self.rss_entry)
                for self.rss_entry in self.parsed_rssfeed.entries
                if self.PATTERN_HASHTAG.findall(self.rss_entry.title)
            ]
            try:
                results = None
                # 使用 asyncio.gather 並行處理
                results = await asyncio.gather(*tasks)
            except Exception as e:
                logger_API_Twitter.error(e)
                raise

            for parallelization in results:
                if parallelization:
                    yield parallelization
                else:
                    raise ValueError(
                        f"Error {parallelization} yield cant't processing RSS entry")

    async def _process_rss_entry(self, rss_entry: Element) -> Union[Tuple[feedparser.FeedParserDict, str, str]:, None]:

        try:
            # 將發布時間轉換為台灣時區
            self.pub_date_tw = await TimeZoneConverter().convert_time(rss_entry.published)
            self.description = rss_entry.description

            return rss_entry, self.pub_date_tw, self.description
        except Exception as e:
            logger.error(f"Error processing RSS entry at description: {e}")
            return None, None, None

    async def process_entry(self, rss_entry: Element) -> None:

        # 從 rss.entries 的描述中提取 Tweet post 的標題
        # 過濾條目中的圖片
        self.filter_entry = self.filter_entry_img(self.description)

        try:
            if self.filter_entry is not None:
                pass
        except ValueError:
            logger.error(
                f"Post title:{self.filter_entry} author_avatar:{self.author_avatar} 其中一項為 None")
            raise ValueError

        try:
            # 處理 Twitter 圖片描述
            twitter_imgs_description, twitter_description_imgs_count = (
                await TwitterHandler._process_tweet_images(self.description)
            )
        except BaseException as e:
            logger.error(f"Error processing tweet images: {e}")
            raise BaseException(
                "TwitterHandler._process_tweet_images 無法處理 entry 中的圖片影片數據"
            )

        # 匹配作者頭像
        self.author_avatar = self.match_author_avatar()
        # 建立 Twitter RSS 字典
        await TwitterHandler.create_twitter_rss_dict(
            rss_entry,
            self.filter_entry,
            self.pub_date_tw,
            int(twitter_description_imgs_count),
            twitter_imgs_description,
            self.author_avatar
        )

    @staticmethod
    async def _process_orig_imgs(twitter_imgs_description: List[str]) -> List[str]:
        # 檢查傳入值是否為 list 型別
        if not isinstance(twitter_imgs_description, list):
            logger.error(f"{twitter_imgs_description} 傳入值必須是 list 型別")
            raise TypeError("檢查 _process_tweet_images replace_qp_url value!")

        for i, url in enumerate(twitter_imgs_description):
            if url.endswith("?format=jpg"):
                twitter_imgs_description[i] += "&name=orig"
        return twitter_imgs_description

    @ staticmethod
    @ lru_cache(maxsize=None)
    async def _process_tweet_images(description: str) -> Tuple[str, int]:

        replace_qp_url = []

        # 使用預先編譯的正則表達式模式來查找所有圖片和影片的URL
        replace_qp_url.extend(
            TwitterHandler.PATTERN_tweet_img.findall(description))
        replace_qp_url.extend(TwitterHandler.PATTERN_mp4.findall(description))

        # 處理圖片和影片的URL列表
        twitter_imgs_description = await TwitterHandler._process_orig_imgs(
            replace_qp_url)

        # 計算圖片和影片的數量
        twitter_description_imgs_count = len(twitter_imgs_description)
        # 將圖片URL列表轉換為字符串，再以空格分割每個圖片URL，以便保存到字典中
        twitter_imgs_description_str = " ".join(twitter_imgs_description)
        # 如果沒有圖片URL，將其設置為 None
        twitter_imgs_description_str = twitter_imgs_description_str if twitter_imgs_description_str else None

        # 錯誤處理判斷是否有圖片或影片，返回None並且 images_count 為 int(0)
        if twitter_imgs_description_str is None:
            logger.info("Twitter post 沒有匹配到任何圖片!")
            return None, 0
        # 啟動條件為開啟類變數 markdown_urls_switch == True
        # 將輸入的URL字符串分割成單獨的URL，並用Markdown格式標記每個URL，前面加上數字和圓括號
        # EX: [1](https://www.example.com/) [2](https://www.example.org/) [3](https://www.iana.org/)
        elif TwitterHandler.markdown_urls_switch is True:
            # 使用.join法，所以列表推導內部迴圈都是字串操作'資料型態'不要認錯，[] 和 () 只是用來Markdown的常數str
            twitter_imgs_description_str = " ".join(
                [f"[{index+1}]({url})" for index,
                 # 列表推導式，將 replace_qp_url 列表中的每個元素，加上數字和圓括號
                    url in enumerate(twitter_imgs_description_str.split(" "))]  # 以空格區分出每個圖片URL
            )
            return str(twitter_imgs_description_str), int(twitter_description_imgs_count)
        else:
            # 返回string格式的描述內容和總圖片數量，每個網址將以空格分隔並且沒有markdown格式
            return str(twitter_imgs_description_str), int(twitter_description_imgs_count)

    @ staticmethod
    @ lru_cache(maxsize=None)
    def filter_entry_img(description: str) -> str:
        # 有檢測錯誤的早返回
        if not description:
            logger.warning(
                f"RSS description {description} is None or fail processing!",
                type(description)
            )
            raise ValueError(
                f'Checking description: |{description}| value status.')

        # 匹配描述中的標籤，直到遇到 <img src="、<video controls=" 或 <video src="
        description_match = TwitterHandler.DESCRIPTION_PATTERN_TAG.search(
            description)

        if not description_match:
            logger.warning(
                "filter_entry_img: 無法解析貼文圖影，可能是該貼文中沒有發布任何相片或影片，或該貼文是轉貼文 ↓\n"
                f"{description}"
            )
            # 對於沒有匹配到圖影的只解析描述，並且將描述中的 <br> 標籤換成換行符號
            description = re.sub(r"<br\s*/?>", "\n",
                                 description)
        else:
            description = re.sub(r"<br\s*/?>", "\n",
                                 description_match.group(1))

        return description  # Tweet Entry or None for no description

    @ lru_cache(maxsize=None)
    def match_author_avatar(self) -> Optional[str]:
        try:
            # 嘗試解析 XML 內容
            xml_data = ET.fromstring(self.http_response_content)
        except ET.ParseError as e:
            # 如果內容不是有效的 XML，記錄錯誤並返回 None
            logger.error(f"ParseError: {e}")
            return None

        # 尋找所有 RSS 中的 <url> 標籤
        raw_xml_urls = xml_data.findall(".//url")

        # 過濾並回傳符合條件的 URL
        for url_element in raw_xml_urls:
            if TwitterHandler.DESCRIPTION_PATTERN_AUTHOR.match(url_element.text):
                return url_element.text

        logger.warning("match_author_avatar: 無法匹配作者頭像，返回空字串")
        return ""  # 如果沒有匹配的URL，返回 空字串

    # 當找到 hashtags 時，調用 process_hashtags 函數
    async def process_hashtags(rss_title: str) -> str:
        # 異步處理每個 hashtag
        # 從 RSS 標題中提取 hashtag
        for _ in rss_title:
            hash_tags = {word for word in rss_title.split()
                         if word.startswith("#")}

            # 呼叫 match_tags 字典函數，傳入 hashtags 列表用來匹配
            # 並返回對應的 IVE 成員名稱，用作後續 Discord 的頻道處理
            matched_values = await match_tags(hash_tags)

            # 如果匹配到多個值，則將 Discord 頻道設為 "GROUPS"
            # 如果沒有匹配到任何值，記錄並拋出錯誤
            if matched_values is None:
                logger.debug(matched_values, hash_tags)
                raise ValueError("Discord channel find fail")
            elif len(matched_values) > 1:
                dc_channel = "GROUPS"
                return dc_channel
            # 如果匹配到單個值，則清理格式並返回
            else:
                matched_values = str(matched_values)
                matched_values = (
                    matched_values.replace("''", "")
                    .replace("'", "")
                    .replace("{", "")
                    .replace("}", "")
                    .replace(", ", ",")
                )
                dc_channel = matched_values
                return dc_channel

    @classmethod
    async def create_twitter_rss_dict(cls, *args, **kwargs) -> Dict[str, Any]:
        # 建立和更新 Twitter RSS 字典
        await cls.Twitter_Dict_Manager.load_from_json()
        twitter_rss_dict = cls.Twitter_Dict_Manager()

        await cls.update_twitter_dict(*args, **kwargs)
        return twitter_rss_dict

    @classmethod
    async def update_twitter_dict(
        cls,
        rss_entry: Element,
        filter_entry: str,
        pub_date_tw: str,
        twitter_description_imgs_count: int,
        twitter_imgs_description: str,
        author_avatar: str
    ) -> None:

        twitter_post_link = rss_entry.link
        dc_channel = await cls.process_hashtags(str(rss_entry.title))

       # 存進字典的 Tuple
        tuple_of_dict = (
            str(rss_entry.author),
            str(rss_entry.link),
            str(filter_entry),  # Tweet post_title
            str(pub_date_tw),
            f"{await get_formatted_current_time()}",
            int(twitter_description_imgs_count),
            str(twitter_imgs_description),
            str(author_avatar),
            str(dc_channel),
        )

        # 把Twitter 貼文網址 MD5當字典的 Key
        MD5 = hashlib.md5(twitter_post_link.encode("utf-8")).hexdigest()

        async def time_offset(match_set_md5=None):
            match_set_md5 = set()

            if len(pub_date_tw) == 19:
                time_diffs = TimeDifferenceCalculator.calculate_in_parallel(
                    [pub_date_tw])
                if len(time_diffs) == 0:
                    logger.info("此RSS貼文超過24小時，不存到字典，可以控制是否開啟")
                elif time_diffs:
                    match_set_md5.add(MD5)
                    twitter_dict = {MD5: tuple_of_dict}

                    # 把字典丟到 update_twitter_dict 方法
                    await cls.Twitter_Dict_Manager.update_twitter_dict(twitter_dict
                                                                       )
            else:
                if isinstance(pub_date_tw, str):
                    logger.warning(
                        f"pub_date_tw: {pub_date_tw} 資料型態正確，檢查是否時間格式錯誤，無法正確計算時間差異")
                    raise ValueError(f"pub_date_tw: {pub_date_tw} 字串時間格式錯誤! ")
                elif isinstance(pub_date_tw, str) is False:
                    logger.warning(
                        f"pub_date_tw: {pub_date_tw} 格式錯誤，無法正確計算時間差異")
                    raise ValueError(
                        f"pub_date_tw: {pub_date_tw} 格式錯誤")
                else:
                    logger.error(
                        f"pub_date_tw 有異常 {pub_date_tw} | {type(pub_date_tw)} | {len(pub_date_tw)} 無法正確計算時間差異")
                    raise ValueError(
                        f"pub_date_tw: {pub_date_tw} 異常，無法正確計算時間差異")

        if TwitterHandler.Dev_24hr_switch is False:
            await asyncio.gather(time_offset())
        else:
            print(
                '\033[38;2;255;230;128m開發者模式開啟，將存到字典，已經跳過\033[0m',
                '\033[38;2;230;230;0m發文 \033[0m\033[38;5;99m24\033[0m \033[38;2;230;230;0m小時內的限製\033[0m'
            )
            await cls.Twitter_Dict_Manager.update_twitter_dict({MD5: tuple_of_dict}
                                                               )

    class Twitter_Dict_Manager:

        # 創建一個類別屬性，用於存儲 Twitter 相關的字典數據
        twitter_dict = {}

        @classmethod
        @cached(ttl=1200, cache=Cache.MEMORY)
        async def load_from_json(cls) -> None:
            json_file = os.path.abspath(
                os.path.join(
                    os.path.dirname(
                        __file__), "..", "assets", "Twitter_dict.json"
                )
            )
            # 檢查文件是否存在且文件大小不為零
            if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
                async with aiofiles.open(json_file, "r") as j:
                    file_content = await j.read()
                    # 如果文件內容不為空，則使用 orjson 加載 JSON 數據
                    cls.twitter_dict = orjson.loads(
                        file_content) if file_content else {}
            else:
                # 如果文件不存在或為空，則初始化為空字典
                cls.twitter_dict = {}

        @classmethod
        async def save_to_json(cls) -> None:
            try:
                json_file = os.path.abspath(
                    os.path.join(
                        os.path.dirname(
                            __file__), "..", "assets", "Twitter_dict.json"
                    )
                )
            except FileNotFoundError:
                logger.error(f"json_file: {json_file} 文件不存在")
                raise FileExistsError(f"json_file: {json_file} 文件不存在")

            # 使用 orjson 進行序列化
            json_data = orjson.dumps(cls.twitter_dict).decode('utf-8')
            # 使用 json 進行格式化輸出，以便於閱讀
            formatted_json_data = json.dumps(json.loads(json_data), indent=4)

            # 保存數據到 pkl 文件
            cls.save_to_pkl(cls.twitter_dict)

            # 將格式化後的 JSON 寫入文件
            async with aiofiles.open(json_file, "w") as j:
                await j.write(formatted_json_data)

        @classmethod
        def save_to_pkl(cls, data: dict) -> None:
            try:
                pkl_file = os.path.abspath(
                    os.path.join(
                        os.path.dirname(
                            __file__), "..", "assets", "Twitter_dict.pkl"
                    )
                )
            except FileExistsError:
                logger.error(f"pkl_file: {pkl_file} 文件不存在")
                raise FileExistsError(f"pkl_file: {pkl_file} 文件不存在")

            with open(pkl_file, "wb") as pkl:
                pickle.dump(data, pkl)
                logger.info(f"{data.keys()} 數據保存到PKL成功")

        @classmethod
        async def update_twitter_dict(cls, new_data: Dict[str, Any]) -> None:
            # 更新類別屬性字典數據
            cls.twitter_dict.update(new_data)
            # 非同步調用 save_to_json 方法將更新後的數據保存到 JSON 文件
            await cls.save_to_json()


class TimeDifferenceCalculator:

    # 類定義台北時區
    TAIPEI_TZ = ZoneInfo("Asia/Taipei")

    # 使用靜態方法計算時間差，並使用 lru_cache 進行緩存以提高效率
    @staticmethod
    @lru_cache(maxsize=64)
    def calculate_time_difference(target_time_str: str) -> float:
        try:
            """
            # 計算時間差（單位：秒）
            CURRENT_TIME = datetime.now().astimezone(TimeDifferenceCalculator.TAIPEI_TZ)
            target_time = datetime.strptime(target_time_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=TimeDifferenceCalculator.TAIPEI_TZ)

            time_difference_seconds = (CURRENT_TIME - target_time) -> Output: float(datetime.strptime(target_time_str, "%Y/%m/%d %H:%M:%S")

            如果計算出的時間差小於24小時（86400秒），則返回該時間差（單位：秒）；否則返回 None
            """
            time_difference_seconds = (
                datetime.now().astimezone(TimeDifferenceCalculator.TAIPEI_TZ) - datetime.strptime(
                    target_time_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=TimeDifferenceCalculator.TAIPEI_TZ)).total_seconds()

            # 如果時間差小於24小時
            if time_difference_seconds <= 86400:
                return time_difference_seconds
            else:
                return None
        except Exception as e:
            logger.error(f"Error calculating time difference: {e}")
            return None

    # 使用靜態方法並行計算多個時間差
    @staticmethod
    def calculate_in_parallel(cal_time_strings: Iterable[Union[str, Tuple[str]]], max_workers: int = 2) -> set:
        # 初始化一個空集合用於存儲結果
        parallelization = set()
        try:
            # 創建一個最大工作數為 max_workers 的線程池
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(
                    TimeDifferenceCalculator.calculate_time_difference, time_str) for time_str in cal_time_strings]
                # 提交計算時間差的任務到線程池
                for future, time_str in zip(as_completed(futures), cal_time_strings):
                    # 獲取任務結果
                    result = future.result()
                    if result is not None:
                        # 將結果添加到集合中
                        parallelization.add(time_str) if isinstance(
                            time_str, str) else parallelization.add(time_str[0])
            return parallelization
        except Exception as e:
            logger.error(f"Error in parallel calculation: {e}")
            # 返回集合（即使發生錯誤也返回已經計算的結果）
            return parallelization


class start_API_Twitter:
    def __init__(self, url):
        self.url = url
        self.rss_object = TwitterHandler(url)

    async def try_url(self) -> bool:
        try:
            await self.rss_object.validate_url_and_get_feed()
        except ValueError:
            logger.warning(" URL 格式錯誤，請檢查後重試")
            return False
        return True

    async def get_response(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        if not await self.try_url():
            return
        try:
            return await self.rss_object.response_content()
        except AttributeError as e:
            logger.error(f"ERROR: {e}")
            raise AttributeError("Error processing RSS feed")


if __name__ == "__main__":

    url = ""
    asyncio.run(start_API_Twitter(url).get_response())
