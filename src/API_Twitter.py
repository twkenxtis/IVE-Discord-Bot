import hashlib
import logging
import os
import pickle

from twitter.API_match_Twitter_account import (
    TwitterAccountProcessor,
    TwitterEntry_Tag_Processor,
    Error_Log_Handler,
)
from twitter.Twitter_rss_process import *


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


Twitter_cache_dict_pkl = "../assets/Twitter_cache_dict.pkl"


class Main_for_twitter:
    def twitter_account_process():
        global Twitter_cache_dict_pkl

        logging.basicConfig(
            level=logging.INFO,
            handlers=[ColoredLogHandler(
                fmt=logging.BASIC_FORMAT, file_path='./logs\\twitter\\log.txt', debug_file_path='./logs\\twitter\\DEBUG_log.txt')],
        )

        # 開發用
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        DEV_PATH = os.path.join('decode_printer.txt')
        # 正式環境需讀取 000003_debin.log 檔案的內容

        # match is Twitter account or not
        match_output_tuple = TwitterAccountProcessor(
            str(DEV_PATH)
        ).process_twitter_account()

        # match twitter entry
        with open(DEV_PATH, 'r', encoding='UTF-8', errors='ignore') as f:
            entry_list = f.read()
            entry_list = TwitterEntry_Tag_Processor.match_twitter_entry(
                entry_list)

        # 初始化要存入cache的list 最終會使用value 'Twitter_cache_list' 清單最為最終值
        saveto_cache_list = []

        def match_twitter_account():
            if match_output_tuple is None and Error_Log_Handler.error_log() is None:
                _list_append_SWITCH = False
                SystemExit(1)
            # match_output_tuple[0] is binary search bool
            elif match_output_tuple[0] is False:
                _list_append_SWITCH = False
                SystemExit(1)
            elif not match_output_tuple is False:
                _list_append_SWITCH = True
                # 網址哈希一下再存進去
                hash_link = hashlib.md5(
                    match_output_tuple[2].encode()
                ).hexdigest()  # 存到Value Twitter_cache_list
                saveto_cache_list.append(match_output_tuple[1])  # 符合的twitter帳號

            if not entry_list is None:
                # 將 entry_list 中的第一個元素以空格分割成單詞列表，選取以 '#' 開頭的單詞，並將它們存儲在列表中
                hashtags = [h for h in entry_list[0].split()
                            if h.startswith('#')]
                # 使用 search_with_hashmap() 類方法搜索關鍵詞
                TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)

                # 如果True Hahtag 都是同一成員的TAG
                if TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)[0] is True:
                    # Boolean value 都是 (hashtags)[0] 返回的匹配成員 value > (hashtags)[0]
                    if not match_output_tuple is False and _list_append_SWITCH is True:
                        # 將運算回來的成員存到List中
                        saveto_cache_list.append(
                            TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)[
                                1][-1:]
                        )
                else:
                    # 如果False就是檢測到多人成員TAG
                    saveto_cache_list.append(str("GROUPS"))

                # list 要同時匹配帳號和IVE TAG 才存入[Twitter_cache_list]
                if len(saveto_cache_list) >= 2:  # At least 2
                    # 把 match Tag 轉成 str 後去除全部 [''] 字元
                    saveto_cache_list[1] = (
                        str(saveto_cache_list[1])
                        .replace("[", "")
                        .replace("]", "")
                        .replace("'", "")
                    )

                    # Twitter_cache_list  ['qcpk0203', 'REI', 'c682e42712551f88dfcefe076e2aeb93']
                    Twitter_cache_list = [
                        saveto_cache_list[0], saveto_cache_list[1], hash_link]

                    def save_to_pkl():
                        # 開始存入 value 到 ../assets/Twitter_cache_dict.pkl
                        os.chdir(os.path.dirname(os.path.abspath(__file__)))
                        try:
                            with open(Twitter_cache_dict_pkl, 'rb') as file:
                                existing_data = pickle.load(file)
                        except FileNotFoundError:
                            with open(Twitter_cache_dict_pkl, 'wb') as pkl:
                                pickle.dump(Twitter_cache_list, pkl)
                                existing_data = []
                            logging.warning(
                                '  /assets/Twitter_cache_dict.pkl 遺失! 已經初始化，程式可能會產生異常'
                            )

                        # 將新的數據追加到現有數據中
                        existing_data.append(Twitter_cache_list)
                        # 將更新後的數據寫入文件
                        with open(Twitter_cache_dict_pkl, 'wb') as file:
                            pickle.dump(existing_data, file)
                        logging.info(
                            f'{Twitter_cache_list} save to pkl successful')

                    save_to_pkl()

                    Twitter.twitter_rss()  # 呼叫HTTP RSS請求和存入字典的操作
                else:
                    Error_Log_Handler.error_log()
                    pass
            else:
                # 沒找到匹配的Tag
                pass
                SystemExit(1)

        match_twitter_account()

    twitter_account_process()


Main_for_twitter()
