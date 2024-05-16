import asyncio
import hashlib
import json
import logging
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse

import http_utility
from custom_log import ColoredLogHandler
from timezone import SystemTime, TimeZoneConverter

import feedparser


class TwitterHandler(object):

    def __init__(self, url: str) -> None:
        self.url = url
        self.http_response_content: str | None = None
        self.parsed_rssfeed = None

    async def validate_url_and_get_feed(self):
        result = urlparse(self.url)
        if not all([result.scheme, result.netloc]):
            print(
                f"\033[38;2;102;153;153mSystem current time: {SystemTime.format_current_time()}\033[0m")
            logging.warning(" URL 格式錯誤，請檢查後重試")
            raise ValueError

        self.http_response_content = await self.start_request(self.url)

    async def start_request(self, rss_url: str) -> str:
        http_requester = http_utility.HttpRequester(rss_url)
        await http_requester.start_requests()
        response_content = await http_requester.get_response_content()
        return response_content

    async def response_content(self) -> tuple[str, dict]:
        loop = asyncio.get_running_loop()
        if self.http_response_content is not None:
            parsed_rssfeed = await loop.run_in_executor(None, feedparser.parse, self.http_response_content)
            self.feedparser(parsed_rssfeed)
            return str(self.http_response_content), dict(parsed_rssfeed)

    def feedparser(self, parsed_rssfeed):

        gmt_converter = TimeZoneConverter("GMT", "Asia/Taipei")

        if parsed_rssfeed is not None:
            # 遍歷RSS描述內容
            for rss_entry in parsed_rssfeed.entries:
                # 轉自訂格式 GMT Sun, 05 May 2024 10:52:35 GMT -> 2024/05/05 10:52:35
                pub_date_tw = gmt_converter.convert_time_gmt_to_utc(
                    rss_entry.published)
                description = rss_entry.description
                # 描述內容比較多要過濾掉多餘的內容，另外用函式處理
                self.process_entry(rss_entry, pub_date_tw, description)

    def process_entry(self, rss_entry, pub_date_tw, description):

        filter_entry = self.filter_entry_img(description)
        author_avatar = self.match_author_avatar(self.http_response_content)

        # 從描述找出所有圖片的URL
        try:
            twitter_imgs_description, twitter_description_imgs_count = TwitterHandler._process_tweet_images(
                description)
        except TwitterHandler.TwitterException as e:
            logging.error(f"Error processing tweet images: {e}")
            raise TwitterHandler.Twitter(
                "TwitterHandler._process_tweet_images 無法處理 entry 中的圖片影片數據")

        self.twitter_rss_dict = self.create_twitter_rss_dict(
            rss_entry,
            filter_entry,
            pub_date_tw,
            int(twitter_description_imgs_count),
            twitter_imgs_description,
            author_avatar
        )

    @staticmethod
    def _process_tweet_images(description):

        # 定義圖片和影片的正則表達式模式
        PATTERN_1 = "https://pbs.twimg.com/"
        PATTERN_2 = "https://pbs.twimg.com/media/"
        PATTERN_3 = "https://video.twimg.com/"
        img_pattern = re.compile(
            rf'{PATTERN_1}[^"\']+?\.(?:jpg)|{PATTERN_2}[^"\']+?\?format=jpg|{PATTERN_3}[^"\']+?\.(?:mp4)'
        )

        # 使用正則表達式在描述中查找所有圖片和影片的URL
        replace_qp_url = img_pattern.finditer(description)

        # 初始化存儲圖片URL的列表
        twitter_imgs_description = []

        # 調用私有方法來處理圖片描述
        twitter_imgs_description = TwitterHandler._process_imgs_videos(
            replace_qp_url)

        # 計算圖片和影片的數量
        twitter_description_imgs_count = len(twitter_imgs_description)

        # 將圖片URL列表轉換為字符串，再以空格分割每個圖片URL，以便保存到字典中
        twitter_imgs_description_str = " ".join(twitter_imgs_description)

        # 如果沒有圖片URL，將其設置為 空字串
        twitter_imgs_description_str = twitter_imgs_description_str if twitter_imgs_description_str else "　"

        # 返回處理後的所有圖片網址和總圖片數量
        return str(twitter_imgs_description_str), int(twitter_description_imgs_count)

    @staticmethod
    def _process_imgs_videos(replace_qp_url):
        twitter_imgs_description = []
        # 遍歷 replace_qp_url 過濾出的所有Twitter描述中的URL
        if replace_qp_url:
            for count in replace_qp_url:
                # 原始URL
                original_url = count.group()

                # 如果URL以 ?format=jpg 結尾
                if original_url.endswith("?format=jpg"):
                    # 在URL末尾添加字串 &name=orig 強製抓取原始圖片大小
                    twitter_imgs_description.append(
                        original_url + "&name=orig")
                else:
                    # 如果URL不以 ?format=jpg 結尾
                    # 則直接將原始URL加入清單中 EX: (Twitter影片/縮圖等等...)
                    twitter_imgs_description.append(original_url)
        return list(twitter_imgs_description)

    @staticmethod
    def filter_entry_img(description):
        if description:
            # 從RSS描述中找出所有的圖片連結
            description = re.search(
                r'((?:.|\n)*?)(?:<img src="|<video controls="|<video src=")', description
            )

            # 從描述中過濾出完整的貼文標題 <br> 標籤，換成 "\n"
            description = re.sub(
                r"<br\s*/?>", "\n", description.group(1)
            )
        else:
            description = "　"
        return str(description)

    def match_author_avatar(self, http_response_content):
        try:
            # 嘗試解析 XML 內容
            xml_data = ET.fromstring(http_response_content)
        except ET.ParseError as e:
            # 如果內容不是有效的 XML，記錄錯誤並返回 None
            logging.error(f"ParseError: {e}")
            return None

        # 尋找所有的 <url> 標籤
        raw_xml_urls = xml_data.findall(".//url")

        # 正則表達式模式，用於匹配作者頭像的 URL
        pattern = r"https://pbs.twimg.com/profile_images/.+\.jpg$"

        # 過濾並回傳符合條件的 URL
        for url_element in raw_xml_urls:
            author_avatar = url_element.text
            if re.match(pattern, author_avatar):
                return author_avatar
        return ""  # 如果沒有匹配的URL，返回 空字串

    @classmethod
    def create_twitter_rss_dict(cls, rss_entry, filter_entry, pub_date_tw, twitter_description_imgs_count, twitter_imgs_description, author_avatar):

        cls.Twitter_Dict_Manager.load_from_json()
        twitter_rss_dict = cls.Twitter_Dict_Manager()

        cls.create_tuple_and_update_dict(
            rss_entry,
            filter_entry,
            pub_date_tw,
            twitter_description_imgs_count,
            twitter_imgs_description,
            author_avatar,
            twitter_rss_dict,
        )
        return twitter_rss_dict

    @classmethod
    def create_tuple_and_update_dict(cls, rss_entry, filter_entry, pub_date_tw, twitter_description_imgs_count, twitter_imgs_description, author_avatar, twitter_rss_dict):

        post_title = filter_entry

        # 存進字典的 Tuple
        tuple_of_dict = (
            str(rss_entry.author),
            str(rss_entry.link),
            str(post_title),
            str(pub_date_tw),
            f"{SystemTime.format_current_time()}",
            int(twitter_description_imgs_count),
            str(twitter_imgs_description),
            str(author_avatar),
        )

        twitter_post_link = rss_entry.link

        # 把Twitter貼文網址MD5當Key
        MD5 = hashlib.md5(twitter_post_link.encode("utf-8")).hexdigest()

        # 把字典丢到 update_twitter_dict
        cls.Twitter_Dict_Manager.update_twitter_dict(
            {str(MD5): tuple(tuple_of_dict)})

    class Twitter_Dict_Manager:

        @classmethod
        def load_from_json(cls):
            filename = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "assets", "Twitter_dict.json"))
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, "r") as json_file:
                    file_content = json_file.read()
                    cls.twitter_dict = json.loads(
                        file_content) if file_content else {}
            else:
                cls.twitter_dict = {}

        @classmethod
        def save_to_json(cls):
            filename = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "assets", "Twitter_dict.json"))
            existing_data = {}
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            existing_data.update(cls.twitter_dict)

            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file, indent=4)

        @classmethod
        def update_twitter_dict(cls, new_data: dict):
            cls.twitter_dict.update(new_data)
            cls.save_to_json()


class start_API_Twitter:
    def __init__(self, url):
        self.url = url
        self.rss_tester = TwitterHandler(url)

    async def try_url(self):
        try:
            await self.rss_tester.validate_url_and_get_feed()
        except ValueError as e:
            return False
        return True

    async def get_response(self):
        if not await self.try_url():
            return
        try:
            return await self.rss_tester.response_content()
        except AttributeError as e:
            logging.error(f"ERROR: {e}")
            raise AttributeError("Error processing RSS feed")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, handlers=[
                        ColoredLogHandler(fmt=logging.BASIC_FORMAT)])

    url = "http://192.168.0.225:8153/air_wyive.xml"
    api_twitter = start_API_Twitter(url)
    response = asyncio.run(api_twitter.get_response())
