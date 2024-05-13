import datetime
import logging
import os
import time

from src.API_Twitter import *
from src.custom_log import ColoredLogHandler
from src.setting import check_chrome_notify_log


class ChromeNotifyLogHandler:
    
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        self.history_path = os.path.join(
            self.project_dir, "assets", "notify_history.txt"
        )
        self.setup_logging()
        self.chrome_003_log, self.history_file = self.initialize_files()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                ColoredLogHandler(
                    fmt=logging.BASIC_FORMAT,
                )
            ],
        )

    def initialize_files(self):
        try:
            boolean, patch_000003_log = check_chrome_notify_log()
            chrome_003_log = patch_000003_log
            history_file = self.read_notify_history_file()
            return chrome_003_log, history_file
        except TypeError as e:
            SystemExit(e)

    def read_notify_history_file(self):
        if not os.path.exists(self.history_path):
            with open(self.history_path, "w", encoding="utf-8"):
                logging.warning("檢測到 notify_history.txt 不存在已建立新檔案！")
        return self.history_path

    def check_file_changes(self):
        file_size = os.path.getsize(self.chrome_003_log)
        while True:
            current_size = os.path.getsize(self.chrome_003_log)
            if current_size != file_size:
                file_size = current_size
                return True
            time.sleep(1)

    def get_new_data(self):
        
        current_time = datetime.now()
        print(current_time)
        
        print("\033[38;2;204;255;102mNotification of Continuous checking...\033[0m")
        
        
        with open(self.chrome_003_log, "r", encoding="utf-8", errors="ignore") as old:
            old_data = old.readlines()
        with open(self.history_file, "r", encoding="utf-8", errors="ignore") as temp:
            temp_data = temp.readlines()
        if len(old_data) < len(temp_data):
            logging.warning("檢測到文件異常，已經重新同步 notify_history.txt")
            logging.warning("路徑：%s", self.history_path)
            with open(
                self.history_file, "w", encoding="utf-8", errors="ignore"
            ) as temp:
                temp.writelines(old_data)
            return old_data  # 返回重新同步後的數據
        if len(old_data) > len(temp_data):
            new_data = old_data[len(temp_data) :]
            with open(
                self.history_file, "a", encoding="utf-8", errors="ignore"
            ) as temp:
                temp.writelines(new_data)
            return new_data
        return None

    def main(self):
        try:
            while True:
                if self.check_file_changes():
                    _new_data = self.get_new_data()
                    if _new_data is not None:
                        format_end_data = "".join(_new_data[1:])
                        format_end_data = str(format_end_data.strip())
                        API_Twitter().process_twitter_account(format_end_data)
                time.sleep(0.5)
        except ValueError as e:
            # 如果沒有Twitter匹配失敗時就返回這個錯誤，然後繼續迴圈
            ChromeNotifyLogHandler().main()
        except Exception as e:
            print('\x1b[33mERROR: 由API_Notify 發出異常:\033[0m')
            logging.warning('其他錯誤')
            print(type(e))
            print(e)
