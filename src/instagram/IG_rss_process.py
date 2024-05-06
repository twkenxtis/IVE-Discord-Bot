import hashlib
import json
import os
import pickle
import re

import feedparser
import http_request

from timezone import SystemTime, TimeZoneConverter


class Instagram:
    def ig_rss():

        ig_rss_dict = IG_Dict_Manager()

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open('../../assets/IG_cache_dict.pkl', 'rb') as f:
            ig_account_name = ''.join(pickle.load(f)[0][1:2]).strip("[]'")

        # Development URL for testing #TODO:URL要改成RSSHUB的網址
        rss_request = [
            f'http://127.0.0.1:8153/{ig_account_name}.xml']  # 開發用網址

        for _ in rss_request:
            each_request = http_request.HTTP3Requester(_)

            # Please keep the number at 1 to avoid rate limiting
            each_request.start_requests(1)  # Default request 1

            if each_request.get_response_content() is not None:
                # GMT to UTC time converter
                gmt_converter = TimeZoneConverter(
                    "GMT", "Asia/Taipei"
                )  # Default ("GMT", "Asia/Taipei")

                # 使用 feedparser 解析 RSS 回應，並使用 get_response_content 方法來獲取回應的內容
                feed = feedparser.parse(each_request.get_response_content())

                for entry in feed.entries:
                    # 對於每個條目（entry），利用 gmt_converter 物件將 GMT格式的發佈時間（entry.published）轉換為本地特定時區的時間（pub_date_tw）

                    pub_date_tw = gmt_converter.convert_time_gmt_to_utc(
                        entry.published)

                    # 將條目的描述文字(entry.description)儲存在變數description中，以便後續處理和分析
                    description = entry.description

                    try:
                        # 使用正則表達式 matches_img_count 在描述 description 中尋找所有符合條件的圖片標籤
                        matches_img_count = r'<img height="\d+"\s+src="https://.*?"\s+/>'
                        # 並將結果存儲在 img_count 中
                        img_count = re.findall(matches_img_count, description)
                    except UnboundLocalError as e:
                        print(
                            f"\033[91mAn error occurred\033[0m \033[1;91m{e}\033[0m")
                        print(
                            f"\033[38;2;255;102;102mPlease check internet connection or RSS feed log to fixup this error.\033[0m \n"
                        )
                        break

                    # 使用正則表達式從描述 (description) 中找出第一個出現的 <img 標籤前的所有文本
                    ig_match = re.search(r"^(.*?)<img ", description)
                    if ig_match:
                        # 提取捕獲到的第一個出現的 <img 標籤前的文本，並將其存儲在 filtered_description 中
                        filtered_description = ig_match.group(1)

                        # 使用正則表達式所有 <br> </br> 標籤替換為換行符 \n 並儲存到 filtered_description 中
                        filtered_description = re.sub(
                            r"<br\s*/?>", "\n", filtered_description
                        )
                    # 如果沒有找到 <img 標籤，則將變數 filtered_description 設為 None
                    elif not ig_match:
                        filtered_description = None

                    # 建立一個 Tuple 用來存放遍歷的每個條目資訊，並將其存儲在 dict_tuple 變數中
                    dict_tuple = (
                        entry.author,
                        entry.link,
                        filtered_description,  # Author content from the post
                        pub_date_tw,  # Asia/Taipei is the timezone of pub_date_tw
                        len(img_count),  # Instagram post image count
                        # system current time.
                        f"{SystemTime.format_current_time()}",
                    )

                    # Line 20 - Class ig_rss_dict and ig_dict Dictionary
                    ig_rss_dict.ig_dict[
                        # In RSS, use the MD5 hash of (entry.link) as the {key} for the dictionary or {dict_tuple}
                        hashlib.md5(entry.link.encode("utf-8")).hexdigest()
                    ] = dict_tuple

                    print(
                        "───────────────────────────────────────────────────────────────────────────────────────\n"
                        # Grey System current time
                        f"\033[90m{SystemTime.format_current_time()}\033[0m",
                        # post link MD5 hash
                        f"\033[0m\033[38;5;218m{hashlib.md5(entry.link.encode('utf-8')).hexdigest()}\033[0m",
                        # Red For Author Name
                        f"\033[38;2;255;102;102m{entry.author}\033[0m\n"
                        # Author content from the post
                        f"{filtered_description.strip()}\n",
                        f"\033\033[38;5;69m{entry.link}\033[0m",  # Blue Link
                        # Asia/Taipei timezone and custom format EX: 240422 22:32
                        f"{pub_date_tw}",
                        # Green The post numbers of photos
                        f"\033[0m\033[38;5;118m{len(img_count)}\033[0m",
                    )

        # 在處理完所有 RSS 條目後保存數據到 JSON 文件中
        # 將 dict_tuple 儲存在 ig_rss_dict.ig_dict Dictionary中，{MD5=key}:{tuple=value}
        ig_rss_dict.save_to_json()  # from Dict_Manager import IG_Dict_Manager


class IG_Dict_Manager:
    def __init__(self):
        self.ig_dict = {}

    def load_from_json(self, filename='../../assets/IG_dict.json'):
        if os.path.exists(filename):
            with open(filename, "r") as json_file:
                self.ig_dict = json.load(json_file)

    def save_to_json(self, filename='../../assets/IG_dict.json'):
        with open(filename, "w") as json_file:
            json.dump(self.ig_dict, json_file, indent=4)
