import asyncio
import hashlib
import json
import logging
import os
import pickle
import pytz
import re
import xml.etree.ElementTree as ET
from datetime import datetime

import feedparser
import src.http_request


class Twitter:
    
    def __init__(self) -> None:
        self.twitter_rss_dict = Twitter_Dict_Manager()
        pass

    def start_request(self, twitter_account_name: str):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        rss_request = f'http://127.0.0.1:1200/twitter/media/{twitter_account_name}?limit=1'
        #rss_request = f"http://127.0.0.1:8153/{twitter_account_name}.xml"

        # 獲得原始的 HTTP 響應內容
        self.http_response_content = self.get_feed(rss_request)
        
        if self.http_response_content is not None:
            
            # 使用 feedparser 解析 RSS 內容
            self.parsed_rssfeed = feedparser.parse(self.http_response_content)

            # 處理解析後的 RSS feed
            self.process_feed(self.parsed_rssfeed)

    def get_feed(self, rss_request: str) -> str:
        each_request = src.http_request.HTTP3Requester(str(rss_request))
        asyncio.run(each_request.start_requests(1))  # How many requests to send at once
        if each_request.get_response_content() is None:
            Twitter_PKL_popup.remove_first_values_from_twitter(1)
            print("\033[91m異常處理中.... PKL Cache 已經清除\033[0m")
        else:
            # HTTP 請求的回應內容
            return str(each_request.get_response_content())

    def process_feed(self, rssfeed):
        gmt_converter = TimeZoneConverter("GMT", "Asia/Taipei")

        if rssfeed is not None:

            # 遍歷RSS描述內容
            for entry in rssfeed.entries:
                # 轉自訂格式 GMT Sun, 05 May 2024 10:52:35 GMT -> 2024/05/05 10:52:35
                pub_date_tw = gmt_converter.convert_time_gmt_to_utc(entry.published)
                description = entry.description

                # 描述內容比較多要過濾掉多餘的內容，另外用函式處理
                self.process_entry(entry, pub_date_tw, description)

    def _process_tweet_images(self, description):

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

        # 遍歷 replace_qp_url 過濾出的所有Twitter描述中的URL
        for count in replace_qp_url:
            # 原始URL
            original_url = count.group()

            # 如果URL以 ?format=jpg 結尾
            if original_url.endswith("?format=jpg"):

                # 在URL末尾添加字串 &name=orig 強製抓取原始圖片大小
                twitter_imgs_description.append(original_url + "&name=orig")
            else:
                # 如果URL不以 ?format=jpg 結尾
                # 則直接將原始URL加入清單中 EX: (Twitter影片/縮圖等等...)
                twitter_imgs_description.append(original_url)

        # 計算圖片和影片的數量
        twitter_description_imgs_count = len(list(twitter_imgs_description))

        # 將圖片URL列表轉換為字符串，以便保存到字典中
        twitter_imgs_description = " ".join(map(str, list(twitter_imgs_description)))

        # 如果沒有圖片URL，將其設置為None
        twitter_imgs_description = (
            None
            if len(list(twitter_imgs_description)) == 0
            else str(twitter_imgs_description)
        )

        # 返回處理後的所有圖片網址和總圖片數量
        return str(twitter_imgs_description), int(twitter_description_imgs_count)

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
        return None  # 如果沒有匹配的URL，返回None

    def process_entry(self, entry, pub_date_tw, description):
        filtered_description_title = self.filter_description(description)
        author_avatar = self.match_author_avatar(self.http_response_content)

        # 從描述找出所有圖片的URL
        twitter_imgs_description, twitter_description_imgs_count = (
            self._process_tweet_images(description)
        )

        # 創建字典 value 的 Tuple 把整理好的資訊全部放進去
        self._create_tuple_and_update_dict(
            entry,
            filtered_description_title,
            pub_date_tw,
            twitter_description_imgs_count,
            twitter_imgs_description,
            author_avatar,
            self.twitter_rss_dict,
        )
        
    def _create_tuple_and_update_dict(
        self,
        entry,
        filtered_description_title,
        pub_date_tw,
        twitter_description_imgs_count,
        twitter_imgs_description,
        author_avatar,
        twitter_rss_dict,
    ):
        # 存進字典的Tuple
        tuple_of_dict = (
            entry.author,
            entry.link,
            filtered_description_title,
            pub_date_tw,
            f"{SystemTime.format_current_time()}",
            twitter_description_imgs_count,
            twitter_imgs_description,
            author_avatar,
        )

        # 把Twitter貼文網址MD5當Key
        MD5 = hashlib.md5(entry.link.encode("utf-8")).hexdigest()
        
        # 把字典丟到update_twitter_dict
        twitter_rss_dict.update_twitter_dict({MD5: tuple_of_dict})

    @staticmethod
    def filter_description(description):

        # 從RSS描述中找出所有的圖片連結
        filtered_description_title = re.search(
            r'((?:.|\n)*?)(?:<img src="|<video controls="|<video src=")', description
        )

        # 從描述中過濾出完整的貼文標題 <br> 標籤，換成 "\n"
        if filtered_description_title:
            filtered_description_title = re.sub(
                r"<br\s*/?>", "\n", filtered_description_title.group(1)
            )
        else:
            filtered_description_title = None
        return str(filtered_description_title)


class Twitter_Dict_Manager:

    def __init__(self, filename="../../assets/Twitter_dict.json"):
        # 初始化 Twitter 字典管理器，設置文件名和字典
        self.twitter_dict = {}
        self.filename = filename
        self.load_from_json()
        pass

    def load_from_json(self):

        # 檢查文件是否存在且大小大於0
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            # 將工作目錄設置為文件所在目錄
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

            # 打開 JSON 文件並讀取其內容
            with open(self.filename, "r") as json_file:
                file_content = json_file.read()

                # 如果文件內容不為空，則將其轉換為字典並賦值給 twitter_dict
                self.twitter_dict = json.loads(file_content) if file_content else {}
        else:
            # 如果文件不存在或大小為0，則初始化 twitter_dict 為空字典
            self.twitter_dict = {}

    def save_to_json(self):
        # 將 Twitter 字典保存到 JSON 文件中
        existing_data = {}
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, "r") as json_file:
                existing_data = json.load(json_file)
        existing_data.update(self.twitter_dict)

        with open(self.filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

    def update_twitter_dict(self, new_data: dict):
        # 更新 Twitter 字典並保存到 JSON 文件中
        self.twitter_dict.update(dict(new_data))
        self.save_to_json()


# 查找所有標籤並匹配IVE成員是誰或不只一人
class TwitterMatcher:

    # 定義類變量，用於指定pickle文件的路徑
    Twitter_cache_dict_pkl = "../../assets/Twitter_cache_dict.pkl"

    def __init__(self):
        # 初始化實例變量match_tags為None，用於儲存匹配到的標籤
        self.match_tags = None
        pass
    
    def start_match(self):
        # 開始匹配流程：首先匹配IVE成員，然後將結果保存至pickle文件
        self.match_ive_members()
        self.save_to_pkl()

    def match_ive_members(self):
        # 從pickle文件讀取數據，然後從JSON文件讀取Twitter字典進行匹配
        with open(self.Twitter_cache_dict_pkl, "rb") as file:
            pkl_data = pickle.load(file)
            
        json_file_path = os.path.join(os.getcwd(), '../../assets', 'Twitter_dict.json')
        
        print('DEBUG from Twitter_rss_process checking json file path in line 263: \n', json_file_path)
        
        with open(json_file_path, "r") as j:
            twitter_dict = json.load(j)

        # 檢查pkl_data是否不為空
        if len(list(pkl_data)) >= 1:
            MD5 = pkl_data[0][1]

            # 如果pkl中的MD5值存在於twitter字典中，則從字典中取出相應值
            if MD5 in twitter_dict:
                value = twitter_dict[MD5]
                post_entry = str(value[2].strip())

                # 從貼文中提取所有以 # 開頭的標籤
                hashtags = [h for h in post_entry.split() if h.startswith("#")]

                # 使用提取的標籤匹配標籤並保存到self.match_tags

                self.match_tags = self.match_twitter_entry(hashtags)

                # 檢測標籤是哪位成員或多位成員 如果是多位成員，硬編碼 ["GROUPS"]

                if self.match_tags[0] is False:
                    self.match_tags = ["GROUPS"]
                elif self.match_tags[0] is True:
                    self.match_tags = list(self.match_tags[1][0])

    def match_twitter_entry(self, hashtags):
        # 調用TwitterEntry_Tag_Processor中的match_twitter_entry函數來匹配標籤
        match_tags = TwitterEntry_Tag_Processor.match_twitter_entry(hashtags)

        if type(match_tags) == bool:
            match_tags = ['None']
            match_tags = list(match_tags)
            return list(match_tags)
        else:
            return list(match_tags)

    def save_to_pkl(self):
        try:
            # 嘗試從pickle文件中讀取現有的數據
            with open(self.Twitter_cache_dict_pkl, "rb") as file:
                existing_data = pickle.load(file)
        except FileNotFoundError:
            # 如果pickle文件不存在，創建一個新的文件並記錄警告信息
            with open(self.Twitter_cache_dict_pkl, "wb") as pkl:
                pickle.dump(self.match_tags, pkl)
                existing_data = []
            logging.warning(
                "  /assets/Twitter_cache_dict.pkl 遺失! 已經初始化，程式可能會產生異常"
            )

        # 如果存在現有數據，將新的匹配標籤追加到數據列表中
        # 更新並添加到最尾部，然後保存到pickle文件
        # [['qcpk0203', 'c682e42712551f88dfcefe076e2aeb93'], ['REI']]
        if len(list(existing_data)) >= 1:
            logging.info(f"資料已存放到PKL Cache.")
            existing_data.append(self.match_tags)
            with open(self.Twitter_cache_dict_pkl, "wb") as file:
                pickle.dump(existing_data, file)


class TimeZoneConverter:

    def __init__(self, from_tz, to_tz):
        # 初始化方法，設定資訊來源的時區'from_tz'和目的地時區'to_tz'，並將這兩個時區物件保留在物件的屬性中
        self.from_tz = pytz.timezone(from_tz)
        self.to_tz = pytz.timezone(to_tz)
        pass

    def convert_time_gmt_to_utc(
        self,
        time_str,
        format="%a, %d %b %Y %H:%M:%S %Z",
        output_format="%Y/%m/%d %H:%M:%S",
    ):
        # 將來源時區的時間字串轉換為目的地時區的時間字串
        time_obj = datetime.strptime(time_str, format)  # 將時間字串解析為datetime物件
        time_obj_from_tz = self.from_tz.localize(time_obj)  # 為時間物件增加來源時區資訊
        time_obj_to_tz = time_obj_from_tz.astimezone(
            self.to_tz
        )  # 將時間物件轉換為目的地時區
        return time_obj_to_tz.strftime(
            output_format
        )  # 將時間物件格式化為字串，並返回轉換後的時間字串

    def format_time_slice(
        self,
        time_str,
        format="%a, %d %b %Y %H:%M:%S %Z",
        output_format="%Y%m%d %H:%M:%S",
    ):
        # 用來將給定的GMT時間字串轉換為在UTC+8時區的特定格式時間字串
        return self.convert_time_gmt_to_utc(
            time_str, format, output_format
        )  # 呼叫時區轉換器進行轉換


class SystemTime:
    
    @staticmethod
    def format_current_time(format_string="%Y/%m/%d %H:%M:%S"):
        time_current = datetime.now()
        return time_current.strftime(format_string)


class TwitterEntry_Tag_Processor:

    @staticmethod
    def match_twitter_entry(hashtags: list):

        # 使用哈希 MAP 搜索
        return TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)

    @classmethod
    def search_with_hashmap(cls, tag_list):

        # 設置當前目錄為工作目錄
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # 讀取 ive_hashtag.pkl 文件
        with open("../../assets/ive_hashtag.pkl", "rb") as _pkl:
            pkl_dict = pickle.load(_pkl)
        found_values = []
        found_flag = False
        is_equal = True

        # 遍歷搜索關鍵詞列表
        for n in tag_list:

            # 將搜索關鍵詞轉換為大寫形式
            n_upper = n.upper()

            # 對於哈希表中的每個鍵，將其轉換為大寫形式進行比較
            for key, value in pkl_dict.items():
                if key == n_upper:
                    found_values.append(value)
                    found_flag = True
        if found_flag:
            # 將找到的值轉換為小寫的嵌套列表
            found_values_lower = [
                [each.lower() for each in sub_list] for sub_list in found_values
            ]

            # 檢查找到的 hashtag 值是否全部相同
            base_list = found_values_lower[0]
            for _ in range(1, len(found_values_lower)):
                if base_list != found_values_lower[_]:
                    is_equal = False
                    break
            return bool(is_equal), list(found_values)
        else:
            # 如果未找到匹配的值，返回 False
            return False


class Twitter_PKL_popup:

    def remove_first_values_from_twitter(count):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../assets/Twitter_cache_dict.pkl",
        )

        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            print("錯誤：找不到檔案")
            return
        try:
            # 讀取 pickle 檔案中的資料
            with open(file_path, "rb") as f:
                loaded_list = pickle.load(f)
        except FileNotFoundError:
            print("錯誤：無法從檔案載入資料")
            return

        # 檢查載入的資料是否為空
        if not loaded_list:
            print("清單已經是空的了")
            return

        # 檢查 count 是否大於清單長度
        if count > len(loaded_list):
            print(f"錯誤：清單長度 ({len(loaded_list)}) 小於指定的數量 ({count})")
            return

        # 移除指定數量的值
        removed_values = []
        for _ in range(count):
            removed_values.append(loaded_list.pop(0))

        # 檢查是否只剩下一個空清單，若是則刪除它
        if len(loaded_list) == 1 and not loaded_list[0]:
            print("只剩下一個空清單，刪除它")
            loaded_list = []

        # 將更新後的資料存回 pickle 檔案
        with open(file_path, "wb") as f:
            pickle.dump(loaded_list, f)
