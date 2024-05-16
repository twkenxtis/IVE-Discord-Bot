from typing import Tuple, List
import asyncio
import aiofiles
import hashlib
import json
import logging
import os
import re
import pickle
import xml.etree.ElementTree as ET
from functools import lru_cache
from typing import Tuple, Dict, Any
from urllib.parse import urlparse

import http_utility
from custom_log import logger_API_Twitter
from ive_hash_tag import match_tags
from timezone import TimeZoneConverter, get_formatted_current_time

import feedparser
import orjson
from loguru import logger


class TwitterHandler(object):

    PATTERN_twitter = re.compile(r'https://pbs.twimg.com/[^"\']+?\.(?:jpg)')
    PATTERN_jpg = re.compile(
        r'https://pbs.twimg.com/media/[^"\']+?\?format=jpg')
    PATTERN_mp4 = re.compile(r'https://video.twimg.com/[^"\']+?\.(?:mp4)')
    DESCRIPTION_PATTERN_TAG = re.compile(
        r'((?:.|\n)*?)(?:<img src="|<video controls="|<video src=")')
    DESCRIPTION_PATTERN_AUTHOR = re.compile(
        r"https://pbs.twimg.com/profile_images/.+\.jpg$")

    def __init__(self, url: str) -> None:
        self.url = url  # 初始化時傳入的 URL
        self.http_response_content: str | None = None  # 儲存 HTTP 回應內容
        self.parsed_rssfeed = None  # 儲存解析後的 RSS Feed

    async def validate_url_and_get_feed(self):
        result = urlparse(self.url)
        if not all([result.scheme, result.netloc]):
            logger.warning(" URL 格式錯誤，請檢查後重試")
            raise ValueError

        self.http_response_content = await self.start_request(self.url)

    async def start_request(self, rss_url: str) -> str:
        # 發送 HTTP 請求並取得回應內容
        http_requester = http_utility.HttpRequester(rss_url)
        await http_requester.start_requests()
        response_content = await http_requester.get_response_content()
        await http_requester.close()
        return response_content

    async def response_content(self) -> Tuple[str, Dict]:
        # 取得並處理 RSS Feed 內容
        if self.http_response_content is not None:
            parsed_rssfeed = await self.parse_feed(self.http_response_content)
            async for rss_entry, pub_date_tw, description in self.feedparser(parsed_rssfeed):
                await self.process_entry(rss_entry, pub_date_tw, description)
            return str(self.http_response_content), dict(parsed_rssfeed)

    async def parse_feed(self, http_response_content: str) -> feedparser.FeedParserDict:
        # 解析 RSS Feed 內容
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, feedparser.parse, http_response_content)

    async def feedparser(self, parsed_rssfeed):
        if parsed_rssfeed is not None:
            for rss_entry in parsed_rssfeed.entries:
                hashtags = re.findall(
                    r'#(IVE|ive)', rss_entry.title, re.IGNORECASE)
                # 確保只有在找到 hashtags 時才繼續執行
                if hashtags:
                    pub_date_tw = await TimeZoneConverter().convert_time(
                        str(rss_entry.published))
                    description = rss_entry.description

                    # 當找到 hashtags 時，調用 process_hashtags 函數
                    # await self.process_hashtags(rss_entry.title)
                    yield rss_entry, pub_date_tw, description

    async def process_entries(self):
        if self.parsed_rssfeed is not None:
            async for rss_entry, pub_date_tw, description in self.feedparser(self.parsed_rssfeed):
                await self.process_entry(rss_entry, pub_date_tw, description)

    async def process_entry(self, rss_entry, pub_date_tw, description):
        filter_entry = self.filter_entry_img(description)
        author_avatar = self.match_author_avatar(self.http_response_content)

        try:
            twitter_imgs_description, twitter_description_imgs_count = await TwitterHandler._process_tweet_images(
                description)
        except BaseException as e:
            logger.error(f"Error processing tweet images: {e}")
            raise BaseException(
                "TwitterHandler._process_tweet_images 無法處理 entry 中的圖片影片數據")

        await TwitterHandler.create_twitter_rss_dict(
            rss_entry,
            filter_entry,
            pub_date_tw,
            int(twitter_description_imgs_count),
            twitter_imgs_description,
            author_avatar
        )

    @staticmethod
    async def _process_imgs_videos(twitter_imgs_description: list):
        twitter_imgs = []
        for url in twitter_imgs_description:
            if url.endswith("?format=jpg"):
                # 在URL末尾添加字符串 &name=orig 以強制獲取原始圖片大小
                twitter_imgs.append(url + "&name=orig")
            else:
                twitter_imgs.append(url)
        return twitter_imgs

    @staticmethod
    @lru_cache(maxsize=None)
    async def _process_tweet_images(description: str) -> Tuple[str, int]:
        # 使用預先編譯的正則表達式模式來查找所有圖片和視頻的URL
        replace_qp_url = []
        replace_qp_url.extend(
            TwitterHandler.PATTERN_twitter.findall(description))
        replace_qp_url.extend(TwitterHandler.PATTERN_jpg.findall(description))
        replace_qp_url.extend(TwitterHandler.PATTERN_mp4.findall(description))

        # 處理圖片和視頻的URL列表
        twitter_imgs_description = await TwitterHandler._process_imgs_videos(
            replace_qp_url)

        # 計算圖片和影片的數量
        twitter_description_imgs_count = len(twitter_imgs_description)

        # 將圖片URL列表轉換為字符串，再以空格分割每個圖片URL，以便保存到字典中
        twitter_imgs_description_str = " ".join(twitter_imgs_description)

        # 如果沒有圖片URL，將其設置為空字符串
        twitter_imgs_description_str = twitter_imgs_description_str if twitter_imgs_description_str else "　"

        # 返回處理後的所有圖片網址和總圖片數量
        return str(twitter_imgs_description_str), int(twitter_description_imgs_count)

    @staticmethod
    @lru_cache(maxsize=None)
    def filter_entry_img(description: str) -> str:
        if description:
            # 從RSS描述中找出所有的圖片連結
            description_match = TwitterHandler.DESCRIPTION_PATTERN_TAG.search(
                description)

            if description_match:
                # 從描述中過濾出完整的貼文標題 <br> 標籤，換成 "\n"
                description = re.sub(
                    r"<br\s*/?>", "\n", description_match.group(1)
                )
            else:
                description = "　"
        else:
            description = "　"

        return str(description)

    @staticmethod
    @lru_cache(maxsize=None)
    def match_author_avatar(http_response_content):
        try:
            # 嘗試解析 XML 內容
            xml_data = ET.fromstring(http_response_content)
        except ET.ParseError as e:
            # 如果內容不是有效的 XML，記錄錯誤並返回 None
            logger.error(f"ParseError: {e}")
            return None

        # 尋找所有的 <url> 標籤
        raw_xml_urls = xml_data.findall(".//url")

        # 過濾並回傳符合條件的 URL
        for url_element in raw_xml_urls:
            if TwitterHandler.DESCRIPTION_PATTERN_AUTHOR.match(url_element.text):
                return url_element.text

        return ""  # 如果沒有匹配的URL，返回 空字串

    async def process_hashtags(rss_title: str) -> str:
        # 異步處理每個 hashtag
        for _ in rss_title:
            hash_tags = {word for word in rss_title.split()
                         if word.startswith("#")}

            matched_values = await match_tags(hash_tags)
            if len(matched_values) > 1:
                dc_channel = "GROUPS"
                return dc_channel
            elif matched_values is None:
                logger.debug(matched_values, hash_tags)
                raise ValueError("Discord channel find fail")
            else:
                matched_values = str(matched_values)
                matched_values = matched_values.replace("''", "").replace(
                    "'", "").replace("{", "").replace("}", "").replace(", ", ",")
                dc_channel = matched_values
                return dc_channel

    @classmethod
    async def create_twitter_rss_dict(cls, rss_entry, filter_entry, pub_date_tw, twitter_description_imgs_count, twitter_imgs_description, author_avatar):
        # 建立和更新 Twitter RSS 字典
        await cls.Twitter_Dict_Manager.load_from_json()
        twitter_rss_dict = cls.Twitter_Dict_Manager()

        await cls.update_twitter_dict(
            rss_entry,
            filter_entry,
            pub_date_tw,
            twitter_description_imgs_count,
            twitter_imgs_description,
            author_avatar,
        )
        return twitter_rss_dict

    @classmethod
    async def update_twitter_dict(cls, rss_entry, filter_entry, pub_date_tw, twitter_description_imgs_count, twitter_imgs_description, author_avatar):

        post_title = filter_entry

        dc_channel = await cls.process_hashtags(str(rss_entry.title))

       # 存進字典的 Tuple
        tuple_of_dict = (
            str(rss_entry.author),
            str(rss_entry.link),
            str(post_title),
            str(pub_date_tw),
            f"{await get_formatted_current_time()}",
            int(twitter_description_imgs_count),
            str(twitter_imgs_description),
            str(author_avatar),
            str(dc_channel),
        )

        twitter_post_link = rss_entry.link

        # 把Twitter貼文網址MD5當Key
        MD5 = hashlib.md5(twitter_post_link.encode("utf-8")).hexdigest()

        # 把字典丟到 update_twitter_dict
        await cls.Twitter_Dict_Manager.update_twitter_dict(
            {str(MD5): tuple(tuple_of_dict)})

    class Twitter_Dict_Manager:

        @classmethod
        async def load_from_json(cls) -> None:
            json_file = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "assets", "Twitter_dict.json"))
            if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
                async with aiofiles.open(json_file, "r") as j:
                    file_content = await j.read()
                    cls.twitter_dict = orjson.loads(
                        file_content) if file_content else {}
            else:
                cls.twitter_dict = {}

        @classmethod
        async def save_to_json(cls) -> None:
            json_file = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "assets", "Twitter_dict.json"))
            existing_data = {}
            if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
                async with aiofiles.open(json_file, "r") as file:
                    existing_data = await file.read()

            existing_data_dict = orjson.loads(
                existing_data) if existing_data else {}

            existing_data_dict.update(cls.twitter_dict)

            json_data = json.dumps(existing_data_dict, indent=4)
            async with aiofiles.open(json_file, "w") as j:
                await j.write(json_data)

            # 同步保存 pkl 文件
            cls.save_to_pkl(existing_data_dict)

        @classmethod
        def save_to_pkl(cls, data: dict) -> None:
            pkl_file = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "assets", "Twitter_dict.pkl"))
            with open(pkl_file, "wb") as pkl:
                pickle.dump(data, pkl)

        @classmethod
        async def update_twitter_dict(cls, new_data: Dict[str, Any]) -> None:
            cls.twitter_dict.update(new_data)
            await cls.save_to_json()


class start_API_Twitter:
    def __init__(self, url):
        self.url = url
        self.rss_object = TwitterHandler(url)

    async def try_url(self):
        try:
            await self.rss_object.validate_url_and_get_feed()
        except ValueError as e:
            return False
        return True

    async def get_response(self) -> Tuple[str, Dict[str, Any]] | None:
        if not await self.try_url():
            return
        try:
            return await self.rss_object.response_content()
        except AttributeError as e:
            logger.error(f"ERROR: {e}")
            raise AttributeError("Error processing RSS feed")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    url = "http://192.168.0.225:8153/air_wyive.xml"
    asyncio.run(start_API_Twitter(url).get_response())
