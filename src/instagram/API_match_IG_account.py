import logging
import json
import os
import pickle
import re
import subprocess

from typing import List


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


class InstagramAccountProcessor:
    def __init__(self, input_data: str):

        logging.basicConfig(
            level=logging.INFO,
            handlers=[ColoredLogHandler(
                fmt=logging.BASIC_FORMAT, file_path='./logs\\instagram\\log.txt', debug_file_path='./logs\\instagram\\DEBUG_log.txt')],
        )

        self.input_data = input_data
        # 檢查輸入資料文件路徑是否為空或存在
        if not input_data:
            logging.warning("Input_data cannot be empty")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.RESTORE_LIST_path = os.path.join(
            "..//restore//restore_rss_list.py")
        self.RESTORE_PKL_path = os.path.join("..//restore//restore_rss_pkl.py")
        self.json_file_path = os.path.join(
            script_dir, "../../config/rss_list.json")
        self.savebin_file_path = os.path.join(
            script_dir, "../../assets/temp/json_file_size.bin")
        self.pickle_file_path = os.path.join(
            script_dir, "../../assets/rss_list.pkl")

    def check_rss_list_status(self):
        RESTORE_LIST_path = self.RESTORE_LIST_path
        json_file_path = self.json_file_path
        savebin_file_path = self.savebin_file_path
        pickle_file_path = self.pickle_file_path

        # 檢查是否存在 rss_list.json 文件
        if os.path.isfile(json_file_path) is False:
            logging.warning(
                "找不到檔案 rss_list.json，已初始化 rss_list.json\n"
                f"請重新於{json_file_path} 重新設定JSON檔案!"
            )
            subprocess.run(['python', RESTORE_LIST_path])
        else:
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

    # 匹配的帳號列表

    def read_account_data() -> List[str]:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        script_dir = os.path.dirname(os.path.abspath(__file__))
        RESTORE_LIST_path = os.path.join("..//restore//restore_rss_list.py")
        RESTORE_PKL_path = os.path.join("..//restore//restore_rss_pkl.py")
        json_file_path = os.path.join(script_dir, "../../config/rss_list.json")
        pickle_file_path = os.path.join(
            script_dir, "../../assets/rss_list.pkl")
        error_printer_path = json_file_path[-21:]

        # 檢查是否存在 rss_list.pkl 文件
        if os.path.isfile(pickle_file_path) is False:
            logging.critical(
                " 檢測到異常，已初始化 /config/rss_list.json "
                f"請重新於{error_printer_path} 重新設定JSON檔案!"
            )
            subprocess.run(['python', RESTORE_LIST_path])
            subprocess.run(['python', RESTORE_PKL_path])
        elif os.path.isfile(pickle_file_path):
            rss_list_pk1 = os.path.join("../../assets/rss_list.pkl")
            with open(rss_list_pk1, 'rb') as f:
                account_list = pickle.load(f)
                return account_list

    @staticmethod
    def find_matching_account(account_list: List[str]):

        def decorator(instagram_processor=None):
            # 定義裝飾器中的包裝函式
            def wrapper(self, **args):
                try:
                    with open(self.input_data, 'r', encoding='UTF-8', errors='ignore') as file:
                        target = file.read()
                except FileNotFoundError:
                    logging.warning(
                        "Input is None or Input didn't match any instagram post.")
                    return None
                try:
                    # {'|'.join(account_list)} 創建一個由account_list列表中的元素接下來，最後 | 把 string 連起來
                    pattern = fr"Instagram\W+({'|'.join(account_list)}).*"
                    match_instagram_account = re.search(pattern, target)
                    # 如果匹配到目標帳戶，則呼叫回調函式處理，否則記錄日誌並回傳 None
                    if match_instagram_account is None:
                        logging.warning(
                            "Input is None or Input didn't match any instagram post.")
                    elif match_instagram_account.group(1) in account_list:
                        return instagram_processor(self, match_instagram_account.group(1))
                except TypeError:
                    print(
                        "\x1b[38;2;255;255;51m異常處理，已經重call API_IG.py ...\x1b[0m")
                    match_instagram_account = ""
                    subprocess.run(['python', './API_IG.py'])
                    SystemExit(1)

            return wrapper

        return decorator

    @find_matching_account(read_account_data())
    def process_account_with_matching(self, instagram_account):
        # 帶有裝飾器的方法，尋找匹配的帳戶並處理
        return instagram_account
