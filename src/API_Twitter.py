# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import asyncio
import hashlib
import json
import logging
import os
import pickle
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import lru_cache
from typing import Tuple, Any, Dict, List, AsyncGenerator, Iterable, Optional, Union
from xml.etree.ElementTree import Element
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from src.custom_log import logger_API_Twitter
from src.http_utility import HttpRequester
from src.ive_hash_tag import match_tags
from src.timezone import TimeZoneConverter, get_formatted_current_time

from aiocache import cached, Cache
# aiocache - Apache License 2.0
# Copyright (c) 2024, Tinche
# For more details, see the LICENSE file included with the distribution
import aiofiles
# aiofiles - BSD 3-Clause License
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
import nest_asyncio
# nest_asyncio - BSD 2-Clause License
# Copyright (c) 2018-2020, Ewald de Wit
# For more details, see the LICENSE file included with the distribution
import orjson
# orjson is used under the MIT License
# Copyright (c) 2024 ijl
# For more details, see the LICENSE file included with the distribution

logging.basicConfig(level=logging.INFO)


class TwitterHandler(object):

    # 開啟/關閉 24 小時開發模式
    Dev_24hr_switch = False  # Default is False

    # 開啟/關閉 轉換 URL 為 Markdown 格式 (For Discord bot)
    markdown_urls_switch = True  # Default is True
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
        self.parsed_rssfeed: feedparser.FeedParserDict | None = (
            None  # 儲存解析後的 RSS Feed
        )
        self.filter_entry = None  # 儲存過濾後的 Tweet 描述內容(標題/照片為主)
        self.rss_entry = None  # 儲存 RSS 條目
        self.description = None  # 儲存 RSS 條目的描述內容
        self.pub_date_tw = None  # RSS 條目的發布時間，由GMT轉換成台灣時區並且自訂為字串格式
        self.author_avatar_link = None  # 儲存作者頭像

    async def validate_url_and_get_feed(self) -> str:
        # 檢查 URL 是否包含協議和主機信息
        result = urlparse(self.url)
        if not all([result.scheme, result.netloc]):
            raise ValueError  # 捕捉在 start_API_Twitter.try_url

        # 通過檢查後將傳入的 self.url 作為參數傳遞給 start_request()
        # 異步發起HTTP請求，並於 start_request 函式中取得回應內容
        await self.start_request()

    async def start_request(self) -> str:
        # 實例化物件 HttpRequester 來建立 HTTP 請求器
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
            # self.parsed_rssfeed 為物件 feedparser.util.FeedParserDict 處理後的結果(dict)
            self.parsed_rssfeed = await self.parse_feed()
            # 清洗 self.parsed_rssfeed -> raw data(dict) 建立個別函數分類字典中的 {key:value}
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
            # 初始化 tasks 的結果為None
            results = None
            # 收集所有符合條目的 tasks
            tasks = [
                self._process_rss_entry(self.rss_entry)
                for self.rss_entry in self.parsed_rssfeed.entries
                if self.PATTERN_HASHTAG.findall(self.rss_entry.title)
            ]
            try:
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
                        f"Error {parallelization} yield cant't processing RSS entry"
                    )

    async def _process_rss_entry(
        self, rss_entry: Element
    ) -> Union[Tuple[feedparser.FeedParserDict, str, str]:, None]:
        try:
            # 將RSS中的發布時間轉換為台灣時區(str)非物件
            self.pub_date_tw = await TimeZoneConverter().convert_time(
                rss_entry.published
            )
            self.description = rss_entry.description
            return rss_entry, self.pub_date_tw, self.description
        # 所有關於 RSS 解析錯誤的錯誤都會在此處處理
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
                f"Post title:{self.filter_entry} author_avatar:{self.author_avatar_link} 其中一項為 None"
            )
            raise ValueError
        try:
            # 處理 Twitter 圖片描述
            twitter_imgs_description, twitter_description_imgs_count = TwitterHandler._process_tweet_images(
                self.description)
        except BaseException as e:
            logger.error(f"Error processing tweet images: {e}")
            raise BaseException(
                "TwitterHandler._process_tweet_images 無法處理 entry 中的圖片影片數據"
            )
        # 匹配作者頭像
        self.author_avatar_link = self.match_author_avatar()
        # 建立 Twitter RSS 字典
        await TwitterHandler.create_twitter_rss_dict(
            self,
            rss_entry,
            self.filter_entry,
            self.pub_date_tw,
            int(twitter_description_imgs_count),
            twitter_imgs_description,
            self.author_avatar_link
        )

    @ staticmethod
    def _process_orig_imgs(twitter_imgs_description: List[str]) -> List[str]:
        # 檢查傳入值是否為 list 型別
        if not isinstance(twitter_imgs_description, list):
            logger.error(f"{twitter_imgs_description} 傳入值必須是 list 型別")
            raise TypeError("檢查 _process_tweet_images replace_qp_url value!")

        # 如果符合條件，強制啟用 Twitter Querry string 的原始圖查詢獲得大圖連結
        return [
            url + "&name=orig" if url.endswith("?format=jpg") else url for url in twitter_imgs_description
        ]

    @ staticmethod
    @ lru_cache(maxsize=None)
    def _process_tweet_images(description: str) -> Tuple[str, int]:

        replace_qp_url = []

        # 使用預先編譯的正則表達式模式來查找所有圖片和影片的URL
        replace_qp_url.extend(
            TwitterHandler.PATTERN_tweet_img.findall(description))
        replace_qp_url.extend(TwitterHandler.PATTERN_mp4.findall(description))

        # 處理圖片和影片的URL列表
        twitter_imgs_description = TwitterHandler._process_orig_imgs(
            replace_qp_url)

        # 計算圖片和影片的數量
        twitter_description_imgs_count = len(twitter_imgs_description)
        # 將圖片URL列表轉換為字符串，再以空格分割每個圖片URL，以便保存到字典中
        twitter_imgs_description_str = " ".join(twitter_imgs_description)
        # 如果沒有圖片URL，將其設置為 None
        twitter_imgs_description_str = twitter_imgs_description_str if twitter_imgs_description_str else None

        # 錯誤處理判斷是否有圖片或影片，返回None並且 images_count 為 int(0)
        match twitter_imgs_description_str:
            case None:
                logger.info("Twitter post 沒有匹配到任何圖片!")
                return None, 0
        # 啟動條件為開啟類變數 markdown_urls_switch == True
        # 若開啟，將輸入的 URL 字符串分割成單獨的 URL，並用 Markdown 格式標記每個 URL，前面加上數字和圓括號
        # 例如：[1](https://www.example.com/) [2](https://www.example.org/) [3](https://www.iana.org/)
            case _ if TwitterHandler.markdown_urls_switch:

                # 使用 .join 方法來合併字符串，因此列表推導式中的每個元素都是字符串操作
                # 注意，[] 和 () 只是用來表示 Markdown 的常數字符串，不要混淆資料型態

                twitter_imgs_description_str = " ".join(
                    # 列表推導式，將 replace_qp_url 列表中的每個元素，加上數字和圓括號
                    [f"[{index+1}]({url})" for index, url in enumerate(
                        # 以空格區分出每個圖片URL
                        twitter_imgs_description_str.split(" ")
                    )]
                )
                # 返回合併後的markdown格式字符串網址和總圖片數量
                return str(twitter_imgs_description_str), int(twitter_description_imgs_count)
            case _:
                # 返回描述內容和總圖片數量，每個網址將以空格分隔並且沒有markdown格式
                return str(twitter_imgs_description_str), int(twitter_description_imgs_count)

    @ staticmethod
    @ lru_cache(maxsize=None)
    def filter_entry_img(description: str) -> str:
        def replace_br_tags(text: str) -> str:
            return re.sub(r"<br\s*/?>", "\n", text)

        # 檢測輸入是否有效
        if not description:
            logger.warning(
                f"RSS description {description} is None or fail processing!",
                type(description)
            )
            raise ValueError(
                f'Checking description: |{description}| value status.')

        # 匹配描述中的標籤
        description_match = TwitterHandler.DESCRIPTION_PATTERN_TAG.search(
            description)

        match description_match:
            case None:
                logger.warning(
                    "filter_entry_img: 無法解析貼文圖影，可能是該貼文中沒有發布任何相片或影片，或該貼文是轉貼文 ↓\n"
                    f"{description}"
                )
                description = replace_br_tags(description)
            case _:
                description = replace_br_tags(description_match.group(1))

        return description  # 返回描述或 None

    @ lru_cache(maxsize=None)
    def match_author_avatar(self, xml_data=None) -> Optional[str]:
        try:
            # 嘗試解析 XML 內容
            xml_data = ET.fromstring(self.http_response_content)
        except ET.ParseError as e:
            # 如果內容不是有效的 XML，記錄錯誤並返回 None
            logger.error(f"ParseError: {e}")
            return None

        # 尋找所有 RSS 中的 <url> 標籤，過濾並回傳符合條件的 URL
        for url_element in xml_data.findall(".//url"):
            if TwitterHandler.DESCRIPTION_PATTERN_AUTHOR.match(url_element.text):
                return url_element.text

        logger.warning("match_author_avatar: 無法匹配作者頭像，返回空字串")
        return " "  # 如果沒有匹配的URL，返回 空字串

    @classmethod
    @ lru_cache(maxsize=14)
    # 傳入值為 RSS 描述中擷取的標題，回傳值為 IVE 成員名稱或是 GROUPS
    def process_hashtags(cls, rss_title: str, matched_values=None) -> str:
        # 集合推導，提取 hashtag
        hash_tags = {H for H in rss_title.split() if H.startswith("#")}

        # 呼叫 match_tags 字典函數，傳入 hashtags 列表用來匹配
        matched_values = match_tags(hash_tags)

        # 處理 matched_values 的情況
        match matched_values:
            # 如果 match_tags 函式回傳值為空字典，表示沒有 IVE 成員，因此回傳 log 記錄錯誤並 raise
            case {}:
                logger.critical(rss_title, matched_values, hash_tags)
                raise ValueError("IVE Members finding from hash tags failed")
            # 如果 match_tags 函式回傳值大於 1，表示有多個 IVE 成員，因此回傳 "GROUPS"
            case values if len(values) > 1:
                return "GROUPS"
            # 否則 match_tags 函式回傳值只有 1 個 IVE 成員，因此回傳該成員名稱
            case values:
                return cls.clean_matched_values(values)

    @classmethod
    def clean_matched_values(cls, matched_values: set) -> str:
        # 字串轉換和清理格式，去除set的花括號和單引號，並以逗號分隔
        return (
            str(matched_values)
            .replace("''", "")
            .replace("'", "")
            .replace("{", "")
            .replace("}", "")
            .replace(", ", ",")
        )

    # 類方法，建立和更新 Twitter RSS 字典
    @classmethod
    async def create_twitter_rss_dict(cls, *args, **kwargs) -> Dict[str, Any]:
        """
        class Twitter_Dict_Manager 會在本地建立兩個字典，放在 assets 資料夾持久化
        Twitter_dict.pkl 和 Twitter_dict.json 兩種字典同步更新，這邊會先呼叫字典的實例
        """
        await cls.Twitter_Dict_Manager.load_from_json()
        twitter_rss_dict = cls.Twitter_Dict_Manager()
        await cls.update_twitter_dict(*args, **kwargs)
        return twitter_rss_dict

    @ lru_cache(maxsize=360)
    async def update_twitter_dict(
        self,
        rss_entry: Element,
        filter_entry: str,
        pub_date_tw: str,
        twitter_description_imgs_count: int,
        twitter_imgs_description: str,
        author_avatar_link: str,
    ) -> None:

        # 取得 IVE 成員名稱或是 GROUPS，用於後續 Discord.py 查字典中對應的頻道 ID
        dc_channel = self.process_hashtags(rss_entry.title)

       # 存進字典的 Tuple
        tuple_of_dict = (
            # (str) Tweet author name
            rss_entry.author,
            # (str) Tweet post link
            rss_entry.link,
            # (str) Tweet post entry
            filter_entry,
            # (str) time of Asia/Taipei not object! EX: 2024/05/20 06:58:33
            pub_date_tw,
            # (str) System current time.
            f"{await get_formatted_current_time()}",
            # (int) Tweet ALL images URL count
            int(twitter_description_imgs_count),
            # (str) Tweet ALL images URL
            twitter_imgs_description,
            # (str) Tweet author avatar URL
            author_avatar_link,
            # (str) ive members name or GROUPS
            dc_channel,
        )

        # 把Twitter 貼文網址 MD5當字典的 Key
        MD5 = hashlib.md5(rss_entry.link.encode("utf-8")).hexdigest()

        async def time_offset(match_set_md5=None):
            match_set_md5 = set()

            # pub_data_tw 是個字串非物件 EX: 2024/05/20 06:58:33
            match len(pub_date_tw):
                # 19 是字典索引value[4](pub_date_tw)的長度
                case 19:
                    time_diffs = TimeDifferenceCalculator.calculate_in_parallel([
                                                                                pub_date_tw])
                    match len(time_diffs):
                        case 0:
                            logger.info("此RSS貼文超過24小時，不存到字典，可以由開發者模式控制是否開啟")
                        case _ if time_diffs:
                            # 將貼文符合條件 24小時內 的貼文MD5存入set
                            match_set_md5.add(MD5)
                            # 以MD5作為字典的{Key: tuple} 使用 update_twitter_dict 異步寫入資料到 Twitter_dict 字典中
                            await self.Twitter_Dict_Manager.update_twitter_dict({MD5: tuple_of_dict})
                # 如果 len(pub_date_tw) != 19 的異常處理區域
                case _:
                    match isinstance(pub_date_tw, str):
                        case True:
                            logger.warning(
                                f"pub_date_tw: {pub_date_tw} 資料型態正確，檢查是否時間格式錯誤，無法正確計算時間差異")
                            raise ValueError(
                                f"pub_date_tw: {pub_date_tw} 字串時間格式錯誤! ")
                        case False:
                            logger.warning(
                                f"pub_date_tw: {pub_date_tw} 格式錯誤，無法正確計算時間差異")
                            raise ValueError(
                                f"pub_date_tw: {pub_date_tw} 格式錯誤")
                        case _:
                            logger.error(
                                f"pub_date_tw 有異常 {pub_date_tw} | {type(pub_date_tw)} | {len(pub_date_tw)} 無法正確計算時間差異")
                            raise ValueError(
                                f"pub_date_tw: {pub_date_tw} 異常，無法正確計算時間差異")

        # :56 可以再類方法自行切換開發者模式跳過時間差計算
        if TwitterHandler.Dev_24hr_switch is False:
            # 異步執行時間差計算
            await asyncio.gather(time_offset())
        else:
            # 開發者模式開啟 用打印的方式提醒開發者
            print(
                '\033[38;2;255;230;128m開發者模式開啟，將存到字典，'
                '已經跳過\033[0m\033[38;2;230;230;0m發文',
                '\033[0m\033[38;5;99m24\033[0m \033[38;2;230;230;0m小時內的限製\033[0m'
            )
            await self.Twitter_Dict_Manager.update_twitter_dict({MD5: tuple_of_dict})

    class Twitter_Dict_Manager:

        # 創建一個類別屬性，用於存儲 Twitter 相關的字典數據
        twitter_dict = {}

        @classmethod
        @cached(ttl=1200, cache=Cache.MEMORY)
        async def load_from_json(cls) -> None:
            json_file = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..", "assets", "Twitter_dict.json"
                )
            )
            while True:
                # 檢查文件是否存在且文件大小不為零
                if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
                    try:
                        async with aiofiles.open(json_file, "r") as j:
                            file_content = await j.read()
                            # 如果文件內容不為空，則使用 orjson 加載 JSON 數據
                            cls.twitter_dict = orjson.loads(
                                file_content
                            )
                        break  # 如果成功加載數據，跳出循環
                    except orjson.JSONDecodeError as e:
                        logger.info(f"JSON 解碼錯誤: {e}")
                        time.sleep(2.5)
                    except Exception as e:
                        logger.info(f"其他錯誤: {e}")
                        time.sleep(2.5)

        @classmethod
        async def save_to_json(cls) -> None:
            try:
                json_file = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..", "assets", "Twitter_dict.json"
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
            cls.save_to_pkl_with_retry(cls.twitter_dict)

            # 將格式化後的 JSON 寫入文件
            async with aiofiles.open(json_file, "w") as j:
                await j.write(formatted_json_data)

        @classmethod
        def save_to_pkl_with_retry(cls, data: dict) -> None:
            max_retries = 26
            retry_count = 0
            retry_wait_time = 0.5

            while retry_count < max_retries:
                try:
                    cls.save_to_pkl(data)
                    return  # 如果保存成功，直接返回
                except PermissionError:
                    logger.info(
                        f"PermissionError: 檔案被佔用，重試中... ({retry_count + 1}/{max_retries})"
                    )
                    retry_count += 1
                    time.sleep(retry_wait_time)
            else:
                logger.error(f"無法儲存文件，已達最大重試次數：{max_retries}")
                raise ("無法保存數據到 PKL 文件，請檢查文件是否被其他程序使用")

        @classmethod
        def save_to_pkl(cls, data: dict) -> None:
            try:
                pkl_file = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..", "assets", "Twitter_dict.pkl"
                    )
                )
            except FileExistsError:
                logger.error(f"pkl_file: {pkl_file} 文件不存在")
                raise FileExistsError(f"pkl_file: {pkl_file} 文件不存在")

            with open(pkl_file, "wb") as pkl:
                pickle.dump(data, pkl)
                logger.info("數據保存到PKL成功")

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
    def calculate_time_difference(target_time_str: str, time_difference_seconds=None) -> float:
        try:
            """
            # 計算時間差（單位：秒）
            CURRENT_TIME = datetime.now().astimezone(TimeDifferenceCalculator.TAIPEI_TZ)
            target_time = datetime.strptime(target_time_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=TimeDifferenceCalculator.TAIPEI_TZ)

            time_difference_seconds = (CURRENT_TIME - target_time) -> Output: float(datetime.strptime(target_time_str, "%Y/%m/%d %H:%M:%S")

            如果計算出的時間差小於24小時（86400秒），則返回該時間差（單位：秒）；否則返回 None
            """
            time_difference_seconds = (
                datetime.now().astimezone(TimeDifferenceCalculator.TAIPEI_TZ)
                - datetime.strptime(target_time_str, "%Y/%m/%d %H:%M:%S").replace(
                    tzinfo=TimeDifferenceCalculator.TAIPEI_TZ
                )
            ).total_seconds()

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
    def calculate_in_parallel(cal_time_strings: Iterable[Union[str, Tuple[str]]], max_workers: int = 4) -> set:
        # 初始化一個空集合用於存儲結果
        parallelization = set()
        try:
            # 創建一個最大工作數為 max_workers 的線程池
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        TimeDifferenceCalculator.calculate_time_difference, time_str
                    )
                    for time_str in cal_time_strings
                ]
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
