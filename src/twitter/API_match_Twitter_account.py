import json
import logging
import os
import pickle
import re
import subprocess
import time


class ColoredLogHandler(logging.StreamHandler):
    def __init__(self, fmt=None, file_path=None, debug_file_path=None):
        # 呼叫父類別的建構函數
        super().__init__()

        # 定義不同等級的顏色映射
        self.color_mapping = {
            logging.DEBUG: '\033[92m',           # 浅绿色
            logging.INFO: '\033[96m',            # 青色
            logging.WARNING: '\033[38;5;214m',   # 金黃色
            logging.ERROR: '\x1b[31m',           # 深红色
            logging.CRITICAL:  '\033[91m',      # 深紫红色
        }
        self.reset_color = '\033[0m'  # 重置颜色
        self._fmt = fmt or logging.BASIC_FORMAT

        # 如果指定了文件路徑，則創建一個文件處理器
        if file_path:
            self.file_handler = logging.FileHandler(file_path)
            self.file_handler.setLevel(logging.WARNING)
            self.file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')
            self.file_handler.setFormatter(self.file_formatter)

        # 如果指定了 debug 文件路徑，則創建一個 debug 文件處理器
        if debug_file_path:
            self.debug_file_handler = logging.FileHandler(debug_file_path)
            self.debug_file_handler.setLevel(logging.DEBUG)
            self.debug_file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')
            self.debug_file_handler.setFormatter(self.debug_file_formatter)

    def format(self, record):
        # 取得日誌訊息的顏色格式
        color_format = (
            f"{self.color_mapping.get(record.levelno, '')}{self._fmt}{self.reset_color}"
        )
        formatter = logging.Formatter(color_format)
        return formatter.format(record)

    def emit(self, record):
        # 將日誌訊息輸出到控制台
        super().emit(record)

        # 如果有文件處理器，則將日誌訊息寫入到文件
        if hasattr(self, 'file_handler') and record.levelno >= logging.WARNING:
            self.file_handler.emit(record)

        # 如果有 debug 文件處理器，則將日誌訊息寫入到 debug 文件
        if hasattr(self, 'debug_file_handler') and record.levelno == logging.DEBUG:
            self.debug_file_handler.emit(record)


class TwitterAccountProcessor:

    logging.basicConfig(
        level=logging.INFO,
        handlers=[ColoredLogHandler
                  (fmt=logging.BASIC_FORMAT, file_path='./logs/twitter/log.txt', debug_file_path='./logs/twitter/DEBUG_log.txt')
                  ],
    )

    def __init__(self, input_data_file):
        self.twitter_account = input_data_file
        # 輸出元組
        self.input_data_file = input_data_file
        self.twitter_username: str | None = None
        self.twitter_post_id: str | None = None
        self.twitter_post_link: str | None = None
        self.found_value: bool | None = None
        self.value_in_list: str | None = None

    def process_twitter_account(self):
        # 檢查檔案是否存在
        if os.path.isfile(self.twitter_account):
            with open(self.twitter_account, "r", encoding="utf-8") as twitter_account_data:
                input_data_file = twitter_account_data.read()

             # 處理 Twitter 帳戶信息
            input_data_file, twitter_username, twitter_post_id = (
                self.process_twitter_account_info(
                    input_data_file,
                    self.twitter_account,
                    self.twitter_username,
                    self.twitter_post_id,
                )
            )
            if twitter_username is not None and twitter_post_id is not None:
                search_value = twitter_username.group(1)
                binary_return_value, value_in_list = self.binary_twitter_account_list(
                    search_value
                )
            if twitter_username is not None and twitter_post_id != "":
                # EX : https://twitter.com/elonmusk/status/314159265358979324
                twitter_post_link = f"https://twitter.com/{twitter_username.group(1)}/status/{twitter_post_id.group(1)}"
                # 這是匹配 Twitter 帳戶元組輸出（元組）
                return (
                    bool(binary_return_value),
                    str(value_in_list),
                    str(twitter_post_link),
                    str(twitter_post_id.group(1)),
                )
            else:
                binary_return_value = None
                value_in_list = None
            if binary_return_value is not None or value_in_list is not None:
                self.binary_twitter_account_list(
                    binary_return_value, value_in_list)
            else:
                # 在實例外部判斷是否有找到值
                pass
        else:
            logging.error(
                f"File '{self.twitter_account}' not found, System exit now")
            SystemExit(1)

    def binary_twitter_account_list(self, input_search_value):
        match_Twitter_account = input_search_value.strip()
        binary_return_value, value_in_list = Twitter_account_list().search(
            str(match_Twitter_account))
        return bool(binary_return_value), str(value_in_list)

    def process_twitter_account_info(
        self, twitter_account_data, twitter_account, twitter_username, twitter_post_id
    ):
        twitter_account = next(
            (
                acct
                for acct in re.finditer(
                    r"title((?:(?!#ive).)*)body", twitter_account_data
                )
            ),
            None,
        )
        # 匹配/user/status/模式的内容
        twitter_username = re.search(
            r"/(?P<user>[A-Za-z0-9_]+)/status/", twitter_account_data
        )
        # 匹配/status/user模式的内容
        twitter_post_id = re.search(
            r"/status/(?P<user>[A-Za-z0-9_]+)", twitter_account_data
        )
        if twitter_username is None:
            twitter_post_id = None
        return twitter_account, twitter_username, twitter_post_id


class TwitterEntry_Tag_Processor:
    @staticmethod
    def match_twitter_entry(input_entry: list):
        entry_list = None
        twitter_entry = None
        # 使用正則表達式找出 Twitter entry
        TWITTER_REGEX = re.findall(
            r'https://twitter.com/.*?tweet\b', input_entry, re.DOTALL)
        TWITTER_REGEX_URL = re.findall(
            r'https://twitter.com/(?:#1tweet|")', input_entry)
        for entry_list in TWITTER_REGEX:
            if entry_list != TWITTER_REGEX_URL[0]:
                twitter_entry = [(entry_list).replace('\n', '')]
        return twitter_entry

    @ staticmethod
    def extract_text(i):
        # 使用正則表達式提取引號包裹的文字
        pattern = r'"[^"]+"'
        match = re.search(pattern, i)
        if match:
            return match.group(0)[1:-1]  # 移除引號
        return None

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


class Error_Log_Handler():
    def __init__(self):
        pass

    def error_log():
        logging.warning("Twitter Account match failed.")
        logging.warning(
            "Can't find Twitter username in target.")
        return

    def tag_error():
        logging.warning("Twitter tag match failed.")


class Twitter_account_list:

    logging.basicConfig(level=logging.INFO, handlers=[ColoredLogHandler()])

    def __init__(self):
        self.pickle_file_path = ['']
        script_dir, json_file_path, savebin_file_path, pickle_file_path = self.check_rss_list_json_file()
        self.check_rss_list_status(script_dir, json_file_path,
                                   savebin_file_path, pickle_file_path)

    def check_rss_list_json_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        RESTORE_LIST_path = os.path.join("./restore/restore_rss_list.py")
        RESTORE_PKL_path = os.path.join("./restore/restore_rss_pkl.py")
        json_file_path = os.path.join(script_dir, "../../config/rss_list.json")
        savebin_file_path = os.path.join(
            script_dir, "../../assets/temp/json_file_size.bin")
        pickle_file_path = os.path.join(
            script_dir, "../../assets/rss_list.pkl")
        error_printer_path = json_file_path[-21:]

        # 檢查是否存在 rss_list.json 文件
        if os.path.isfile(json_file_path) is False:
            logging.error(
                " 檢測到json異常，已初始化 /config/rss_list.json "
                f"請重新於{error_printer_path} 重新設定JSON檔案!"
            )
            subprocess.run(['python', RESTORE_LIST_path])
        # 檢查是否存在 rss_list.pkl 文件
        elif os.path.isfile(pickle_file_path) is False:
            logging.critical(
                " 檢測到pkl異常，已初始化 /config/rss_list.json "
                f"請重新於{error_printer_path} 重新設定JSON檔案!"
            )
            subprocess.run(['python', RESTORE_LIST_path])
            subprocess.run(['python', RESTORE_PKL_path])
            time.sleep(1)
        else:
            # 預留空白區域
            pass

        return script_dir, json_file_path, savebin_file_path, pickle_file_path

    def binary_search(self, low, high, value):
        if low <= high:
            mid = (low + high) // 2
            guess = self.pickle_file_path[mid]

            if guess == value:
                if guess == '':
                    return False, 'Not found'
                else:
                    return True, guess
            elif guess < value:
                return self.binary_search(mid + 1, high, value)
            else:
                return self.binary_search(low, mid - 1, value)
        else:
            return False, 'Not found'

    def search(self, value):
        return self.binary_search(0, len(self.pickle_file_path) - 1, value)

    def check_rss_list_status(self, script_dir, json_file_path, savebin_file_path, pickle_file_path):
        with open(str(json_file_path), 'r') as j:
            json_data = json.load(j)
            # 將 json_data 中的空值 (None) 替換為 None，以便後續處理
            processed_json = [i if i else None for i in json_data]

        # 讀取 JSON 檔案的大小，並將其存儲在 current_file_size 變數中
        current_file_size = os.path.getsize(json_file_path)
        # 讀取二進製檔案 savebin_file_path 的內容，並將其轉換為整數 previous_file_size
        with open(savebin_file_path, "rb") as f:
            previous_file_size = int.from_bytes(f.read(), "big")
        # 將 current_file_size 轉換為二進製數據，並寫入到 savebin_file_path 檔案中
        with open(savebin_file_path, "wb") as f:
            f.write(current_file_size.to_bytes(4, "big"))

        # 檢測 rss_list.json 檔案大小是否有變化
        file_size_changed = current_file_size != previous_file_size
        if file_size_changed:
            print(
                f"\033[38;2;255;26;175mJSON file size changed:\033[0m \033[38;2;128;255;255m{file_size_changed}\033[0m")
            # 存入 pickle 檔案，只存入非 None 值
            filtered_json_for_pickle = [
                item for item in processed_json if item is not None]
            if filtered_json_for_pickle:
                # 更新 JSON 資料轉換為 pickle 格式
                with open(pickle_file_path, 'wb') as pickle_file:
                    pickle.dump(filtered_json_for_pickle, pickle_file)
                    logging.info(
                        "rss_list.json transformed to rss_list.pkl successfully!")
                    self.pickle_file_path = pickle_file_path

        # main code for binary search data
        path_to_pk1 = os.path.join(script_dir, '../../assets/rss_list.pkl')
        with open(path_to_pk1, 'rb') as _pickle:
            self.pickle_file_path = pickle.load(_pickle)
            self.pickle_file_path = sorted(self.pickle_file_path)
