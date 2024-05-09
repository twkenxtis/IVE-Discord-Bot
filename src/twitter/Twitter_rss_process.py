import hashlib
import json
import logging
import os
import pickle
import pytz
import re
from datetime import datetime

import feedparser

import http_request


class Twitter:

    @staticmethod
    def twitter_rss(twitter_account_name):

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        twitter_rss_dict = Twitter_Dict_Manager()

        # RSSHUB request
        rss_request = f'http://127.0.0.1:8153/{twitter_account_name}.xml'

        each_request = http_request.HTTP3Requester(rss_request)

        # 使用 start_requests 方法發起請求，並且設定重試次數為1，避免被網站的流量限制
        # Please keep the number at 1 to avoid rate limiting
        each_request.start_requests(1)  # Default request 1

        if each_request.get_response_content() is None:
            Twitter_PKL_popup.remove_first_values_from_twitter(1)
            print('\x1b[91m異常處理中.... PKL Cache 已經清除\x1b[0m')
        else:
            gmt_converter = TimeZoneConverter(
                "GMT", "Asia/Taipei"
            )  # Default ("GMT", "Asia/Taipei")

        # 使用 feedparser 解析 RSS 回應，並使用 get_response_content 方法來獲取回應的內容
            feed = feedparser.parse(each_request.get_response_content())

            for entry in feed.entries:
                # 對於每個條目(entry)，利用 gmt_converter 物件將 GMT格式的發佈時間 (entry.published) 轉換為本地特定時區的時間(pub_date_tw)

                pub_date_tw = gmt_converter.convert_time_gmt_to_utc(
                    entry.published)

                # 將條目的描述文字(entry.description)儲存在變數description中，以便後續處理和分析
                description = entry.description

                # 定義Twitter URL常量，用於正則表達式模式
                TWITTER_BASE_URI = r"https://pbs.twimg.com/"
                TWITTER_MEDIA_URI = r"https://pbs.twimg.com/media/"
                TWITTER_TWEET_VIDEO_URI = r"https://video.twimg.com/tweet_video/"

                # 使用正則表達式來匹配在 Twitter描述 (description) 中匹配所有圖片和影片的URL
                img_pattern = re.compile(
                    rf'{TWITTER_BASE_URI}[^"\']+?\.(?:jpg)|{TWITTER_MEDIA_URI}[^"\']+?\?format=jpg|{TWITTER_TWEET_VIDEO_URI}[^"\']+?\.(?:mp4)'
                )

                # 使用 re.finditer 方法匹配所有匹配項，並將結果存儲在 replace_media_str 變數中
                replace_qp_url = img_pattern.finditer(description)

                # 初始化列表以供存儲 twitter_imgs_description 格式化的 URL
                twitter_imgs_description = []

                # 獲取匹配到的 URL 將 '?&amp;name=orig' 替換為空字符串 (List comprehension) 賦予List新的匹配值
                for _ in replace_qp_url:
                    twitter_imgs_description.append(
                        _.group().replace("&amp;name=orig", ""))

                # 計算有多少張照片或影片，並將其存儲在 twitter_description_imgs_count 變數中
                twitter_description_imgs_count = len(
                    twitter_imgs_description)

                """    
                將 twitter_imgs_description List中的每個元素都轉換為String，然後使用空格將這些String連接起來，得到最終的結果字符串
                使用 .join(...) 將 map() 函數返回的結果列表中的元素連接為一個字符串，並在元素之間添加一個空格
                然後，將連接後的字符串重新賦值給 twitter_imgs_description 變數
                最終，得到有空格分開的Twitter圖片或影片的網址
                """
                twitter_imgs_description = ' '.join(
                    map(str, twitter_imgs_description))

                # 如果正則表達式沒有匹配到圖片或影片的URL，twitter_imgs_description 會是 None
                twitter_imgs_description = None if len(
                    twitter_imgs_description) == 0 else twitter_imgs_description

                # 如果正則表達式匹配到 twitter_imgs_description 僅有圖片貼文的 URL，將提取的Twitter圖片的URL中的jpg格式轉換為webp格式
                # EX: https://pbs.twimg.com/media/example?format=jpg -> https://pbs.twimg.com/media/example?format=jpg&name=orig
                twitter_imgs_description = re.sub(
                    r"(https://pbs\.twimg\.com/media/[^/?]+)\?format=jpg",
                    r"\1?format=jpg&name=orig",
                    twitter_imgs_description,
                )

                # 針對 description 捕獲所有 <img src=" 或 <video controls=" 或 <video src=" 之前的所有內容，傳遞給 filtered_description_title 變數
                filtered_description_title = re.search(
                    r'((?:.|\n)*?)(?:<img src="|<video controls="|<video src=")',
                    description,
                )

                # 只提取匹配結果中的第一個捕獲組的內容，並將其存儲在 filtered_description_title 變數中
                if filtered_description_title:
                    # re 把 description 中所有的 <br> <br/> 標籤換成換行符號
                    filtered_description_title = re.sub(
                        r"<br\s*/?>", "\n", filtered_description_title.group(1))
                else:
                    filtered_description_title = None

                # 建立一個 Tuple 用來存放遍歷的每個條目資訊，並將其存儲在 dict_tuple 變數中
                tuple_of_dict = (
                    entry.author,
                    entry.link,
                    filtered_description_title,  # Author content from the post
                    pub_date_tw,  # Asia/Taipei is the timezone of pub_date_tw
                    # system current time.
                    f"{SystemTime.format_current_time()}",
                    twitter_description_imgs_count,  # How many photo from post
                    twitter_imgs_description,  # Photo from Twitter post
                )

                twitter_rss_dict.twitter_dict[hashlib.md5(
                    entry.link.encode("utf-8")).hexdigest()] = tuple_of_dict

                print(
                    "───────────────────────────────────────────────────────────────────────────────────────\n"
                    # Grey System current time
                    f"\033[90m{SystemTime.format_current_time()}\033[0m",
                    # post link MD5 hash
                    f"\033[0m\033[38;5;218m{hashlib.md5(entry.link.encode('utf-8')).hexdigest()}\033[0m",
                    # Red For Author Name
                    f"\033[38;2;255;102;102m{entry.author}\033[0m\n"
                    # Author content from the post
                    f"{filtered_description_title.strip()}\n",
                    # Photo from Twitter post
                    f"\033[38;2;255;194;153m{twitter_imgs_description}\033[0m\n",
                    f"\033\033[38;5;69m{entry.link}\033[0m",  # Blue Link
                    # Asia/Taipei timezone and custom format EX: 240422 22:32
                    f"{pub_date_tw}",
                    # Green The post numbers of photos
                    f"\033[0m\033[38;5;118m{twitter_description_imgs_count}\033[0m",
                )

                # 在處理完所有 RSS 條目後保存數據到 JSON 文件中
                # 將 dict_tuple 儲存在 twitter_dict.twitter_dict Dictionary中，{MD5=key}:{tuple=value}
                MD5 = hashlib.md5(entry.link.encode('utf-8')).hexdigest()
                twitter_rss_dict.update_twitter_dict({MD5: tuple_of_dict})

                os.chdir(os.path.dirname(os.path.abspath(__file__)))
                Twitter_cache_dict_pkl = '../../assets/Twitter_cache_dict.pkl'

            def match_ive_members():
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
                Twitter_cache_dict_pkl = '../../assets/Twitter_cache_dict.pkl'

                with open(Twitter_cache_dict_pkl, 'rb') as file:
                    pkl_data = pickle.load(file)

                if os.path.isfile('../../assets/Twitter_dict.json'):
                    with open('../../assets/Twitter_dict.json', 'r') as j:
                        twitter_dict = json.load(j)

                MD5 = pkl_data[0][1]
                if MD5 in twitter_dict:
                    value = twitter_dict[MD5]
                    post_entry = str(value[2].strip())

                hashtags = [h for h in post_entry.split() if h.startswith('#')]

                match_tags = TwitterEntry_Tag_Processor.match_twitter_entry(
                    hashtags)
                if match_tags is False:
                    match_tags = list('GROUPS')
                    return match_tags
                elif len(match_tags) > 1:
                    match_tags = list(match_tags[1][0])
                    return match_tags

            def save_to_pkl(match_tags):
                # 開始存入 value 到 /assets/Twitter_cache_dict.pkl
                try:
                    with open(Twitter_cache_dict_pkl, 'rb') as file:
                        existing_data = pickle.load(file)
                except FileNotFoundError:
                    with open(Twitter_cache_dict_pkl, 'wb') as pkl:
                        pickle.dump(match_tags, pkl)
                        existing_data = []
                    logging.warning(
                        '  /assets/Twitter_cache_dict.pkl 遺失! 已經初始化，程式可能會產生異常'
                    )

                # 將新的數據追加到現有數據中
                existing_data.append(match_tags)

                # 將更新後的數據寫入文件
                with open(Twitter_cache_dict_pkl, 'wb') as file:
                    pickle.dump(existing_data, file)

            save_to_pkl(match_ive_members())


class Twitter_Dict_Manager:
    def __init__(self, filename='../../assets/Twitter_dict.json'):
        self.twitter_dict = {}
        self.filename = filename
        self.load_from_json()

    def load_from_json(self):
        if os.path.exists(self.filename):
            if os.path.getsize(self.filename) > 0:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
                with open(self.filename, "r") as json_file:
                    file_content = json_file.read()
                    if file_content:
                        self.twitter_dict = json.loads(file_content)
            else:
                self.twitter_dict = {}

    def save_to_json(self):
        # 讀取現有的JSON數據
        existing_data = {}
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, "r") as json_file:
                existing_data = json.load(json_file)

        # 將新數據追加到已有數據中
        existing_data.update(self.twitter_dict)

        # 寫入JSON檔案
        with open(self.filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

    def update_twitter_dict(self, new_data):
        self.twitter_dict.update(new_data)
        self.save_to_json()


class TimeZoneConverter:
    def __init__(self, from_tz, to_tz):

        self.from_tz = pytz.timezone(from_tz)
        self.to_tz = pytz.timezone(to_tz)

    def convert_time_gmt_to_utc(
        self, time_str, format="%a, %d %b %Y %H:%M:%S %Z", output_format="%y%m%d %H:%M"
    ):
        # A time conversion method that converts a time string in a given time zone to a time string in a specified format in another time zone.

        time_obj = datetime.strptime(
            time_str, format
        )  # Parsing a time string into a datetime object
        time_obj_from_tz = self.from_tz.localize(
            time_obj
        )  # Add source time zone information to the time object
        time_obj_to_tz = time_obj_from_tz.astimezone(
            self.to_tz
        )  # Convert the time object to the target time zone.
        return time_obj_to_tz.strftime(
            output_format
        )  # Format the time object as a string and return the converted time string.

    def format_time_slice(
        self, time_str, format="%a, %d %b %Y %H:%M:%S %Z", output_format="%y%m%d %H:%M"
    ):
        # Time conversion method to convert a given GMT time string to a time string in a specified format in the UTC+8 time zone.

        return self.convert_time_gmt_to_utc(
            time_str, format, output_format
        )  # Call the time zone converter for conversion


class SystemTime:
    @staticmethod
    def format_current_time(format_string="%m/%d %H:%M:%S"):
        time_current = datetime.now()
        return time_current.strftime(format_string)


class TwitterEntry_Tag_Processor:
    @staticmethod
    def match_twitter_entry(hashtags: list):
        hashtag_str = ' '.join(hashtags)
        return TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)

    @ classmethod
    def search_with_hashmap(cls, tag_list):
        # 設定當前的路徑為工作目錄
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        # 讀取 ive_hashtag.pkl 文件
        with open('../../assets/ive_hashtag.pkl', 'rb') as _pkl:
            pkl_dict = pickle.load(_pkl)

        found_values = []
        found_flag = False
        is_equal = True

        # 遍歷搜索關鍵詞列表
        for n in tag_list:
            # 將搜索鍵轉換為大寫形式
            n_upper = n.upper()
            # 對於哈希表中的每個鍵,將其轉換為大寫形式進行比較
            for key, value in pkl_dict.items():
                if key == n_upper:
                    found_values.append(value)
                    found_flag = True

        if found_flag:
            # 將找到的值轉換為小寫的嵌套列表
            found_values_lower = [
                [each.lower() for each in sub_list] for sub_list in found_values
            ]
            # 比較找到的 hashtag 值是否全部相同
            base_list = found_values_lower[0]
            for _ in range(1, len(found_values_lower)):
                if base_list != found_values_lower[_]:
                    is_equal = False
                    break
            return is_equal, found_values
        else:
            return False


class Twitter_PKL_popup:
    def remove_first_values_from_twitter(count):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "../../assets/Twitter_cache_dict.pkl"
        )

        if not os.path.exists(file_path):
            print("Error: File not found.")
            return
        try:
            with open(file_path, "rb") as f:
                loaded_list = pickle.load(f)
        except FileNotFoundError:
            print("Error: Unable to load data from file.")
            return
        if not loaded_list:
            print("List is empty now.")
            return
        if count > len(loaded_list):
            print(
                f"Error: List length ({len(loaded_list)}) is smaller than count ({count})."
            )
            return
        removed_values = []
        for _ in range(count):
            removed_values.append(loaded_list.pop(0))
        if len(loaded_list) == 1 and not loaded_list[0]:
            print("Only one empty list remaining. Deleting it.")
            loaded_list = []
        with open(file_path, "wb") as f:
            pickle.dump(loaded_list, f)
