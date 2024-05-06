import glob
import hashlib
import json
import logging
import os
import pickle
import time

import instaloader

from instagram.API_notify_IG_filter import InstagramFilter
from instagram.API_match_IG_account import InstagramAccountProcessor
from instagram.IG_rss_process import Instagram


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


class Main_for_instagram:

    def ig_account_process():

        logging.basicConfig(
            level=logging.INFO,
            handlers=[ColoredLogHandler(
                fmt=logging.BASIC_FORMAT, file_path='../logs\\instagram\\log.txt', debug_file_path='../logs\\instagram\\DEBUG_log.txt')],
        )

        # 開發用
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        chrome_000003_log = os.path.join('decode_printer.txt')

        # 正式環境需讀取 000003_debin.log 檔案的內容，並將其賦予為 input_IG_notify_data
        with open(
            "decode_printer.txt", "r", encoding="latin1", errors="ignore"
        ) as file:
            InstagramFilter.input_IG_notify_data = (
                file.read().strip()
            )  # 讀取開發用檔案 decode_printer.txt 並去除內容中的空白

        IG_Account_name = InstagramAccountProcessor(
            str(chrome_000003_log)
        ).process_account_with_matching()

        if IG_Account_name is None:
            SystemExit(1)
        else:
            IG_link_id_List = InstagramFilter.main()
            # ['C6BmbFHSkE5', 'fallingin__fall, https://www.instagram.com/p/C6BmbFHSkE5/']
            Ig_cache_List = [IG_link_id_List[1],
                             IG_Account_name, IG_link_id_List[0]]
            file_path_cache = '../assets/IG_cache_dict.pkl'

            # 初始化 loaded_IG_cache_dict 如果 List 是空的把 file_path_cache 內容重置為空
            if os.path.exists(file_path_cache):
                with open(file_path_cache, 'rb') as f:
                    loaded_IG_cache_dict = pickle.load(f)
            elif not loaded_IG_cache_dict:
                with open(file_path_cache, 'wb') as f:
                    f.truncate(0)

            # 添加新的 Ig_cache_List
            loaded_IG_cache_dict.append(Ig_cache_List)

            # 將更新後的 loaded_IG_cache_dict 寫回文件
            with open(file_path_cache, 'wb') as f:
                pickle.dump(loaded_IG_cache_dict, f)
            logging.info(f'{loaded_IG_cache_dict} save to pkl successful')

            # 從文件中讀取第一個元素
            with open('../assets/IG_cache_dict.pkl', 'rb') as f:
                insta_media_id = ''.join(pickle.load(f)[0][0:1]).strip("[]'")
            dir_file_path = f'../assets/images/instagram/{insta_media_id}'

            """
            L = instaloader.Instaloader()
            # EX: https://www.instagram.com/p/C6BmbFHSkE5/
            try:
                os.makedirs(dir_file_path)
            except OSError:
                if not os.path.exists(dir_file_path):
                    raise (f'無法在{dir_file_path}建立資料夾')

            time.sleep(0.3)

            L = instaloader.Instaloader(dirname_pattern=dir_file_path)

            # Create a Post object from the shortcode
            post = instaloader.Post.from_shortcode(L.context, insta_media_id)

            # Download the post
            L.download_post(post, target=insta_media_id)
            """

            Instagram.ig_rss()  # 發起Http請求 + RSSHUB + 檢查是否通知來自IG，最後存到字典中

            def check_directory_exists(path, attempts=30):

                if attempts == 0:
                    return False
                if os.path.exists(path):
                    # 尋找匹配的文件
                    matched_files = [
                        _
                        for _ in ("*.txt", "*.jpg", "*.xz")
                        if glob.glob(os.path.join(path, _))
                    ]

                    # 如果Instadownloads項目都存在，返回True；否則返回False
                    if len(matched_files) == 3:
                        return True
                # 如果檢查失敗，則等待一段時間後進行遞迴檢查
                time.sleep(0.05)
                return check_directory_exists(path, attempts - 1)

            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            instadownloads_file_path = os.path.join(
                f'../assets/images/instagram/{insta_media_id}'
            )

            if check_directory_exists(instadownloads_file_path) is True:
                logging.info("Instaloader Downloads successful.")
                pass
            else:
                logging.warning("Instaloader Downloads failed.")

            """
            def check_dict_value():
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
                with open('../assets/IG_dict.json', 'r') as j:
                    ig_dict = json.load(j)
                with open('../assets/IG_cache_dict.pkl', 'rb') as f:
                    temp = pickle.load(f)

                if len(temp) > 0:
                    # 取第一個元素的第 2 到第 3 個字符取出並轉換為字符串後連接起來，再去除方括號和單引號
                    ig_link = ''.join(str(temp[0][2:3])).strip("[]'") + '/'
                    # 將ig_link字符串進行MD5哈希計算
                    ig_link = hashlib.md5(ig_link.encode()).hexdigest()

                    # 要比對的key
                    desired_key = ig_link
                    # 檢查desired_key是否存在於字典中並以布林值的形式打印比對結果
                    key_exists = desired_key in ig_dict
                    return key_exists

            def remove_first_values_from_ig(count):
                # 內部函數：刪除列表的前 count 個值
                def remove_first_values(data, count):
                    # 如果列表為空，則直接返回空列表
                    if not data:
                        return []

                    # 如果 count 大於列表長度，則返回空列表
                    if count > len(data):
                        logging.warning(
                            f"Error: List length ({len(data)}) is smaller than count ({count})."
                        )
                        return []

                    # 創建一個空列表，存儲被刪除的值
                    removed_values = []
                    for _ in range(count):
                        removed_values.append(data.pop(0))

                    return removed_values

                file_path_cache = os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), '../assets/IG_cache_dict.pkl')

                if not os.path.exists(file_path_cache):
                    logging.warning(
                        "Error: /assets/IG_cache_dict.pkl not found."
                    )
                    return

                try:
                    with open(file_path_cache, 'rb') as f:
                        loaded_list = pickle.load(f)
                except FileNotFoundError:
                    logging.warning(
                        "Error: Unable to load /assets/IG_cache_dict.pkl"
                    )
                    return

                # 檢查 count 是否大於列表長度
                if count > len(loaded_list):
                    logging.warning(
                        f"Error: List length ({len(loaded_list)}) is smaller than count ({count}).")
                    return

                # 刪除 loaded_list 前 count 個值
                remove_first_values(loaded_list, count)

                # 如果 loaded_list 長度為 1 且第一個元素為空列表，則刪除 loaded_list
                if len(loaded_list) == 1 and not loaded_list[0]:
                    logging.INFO("Only one empty list remaining. Deleting it.")
                    loaded_list = []

                with open(file_path_cache, 'wb') as f:
                    pickle.dump(loaded_list, f)
            # 如果字典中已經確認此筆HASH的Key
            if check_dict_value():
                # pop up 第一筆 /assets/IG_cache_dict.pkl 資料
                remove_first_values_from_ig(1)
                """

    ig_account_process()


Main_for_instagram()
