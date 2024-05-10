import hashlib
import logging
import os
import pickle

from custom_log import ColoredLogHandler
from twitter.API_match_Twitter_account import (
    TwitterAccountProcessor,
    Error_Log_Handler,
)
from twitter.Twitter_rss_process import *

#TODO:未來可能寫 TOML 或 Table文件來寫白名單
# 是否開啟轉推阻擋功能 Default: False
re_Tweet_switch = True


class API_Twitter:
    
    def __init__(self):
        self.Twitter_cache_list = []
        self.Twitter_cache_dict_pkl = "../assets/Twitter_cache_dict.pkl"

    @staticmethod
    def match_twitter_account():

        logging.basicConfig(
            level=logging.INFO,
            handlers=[ColoredLogHandler(
                fmt=logging.BASIC_FORMAT, file_path='./logs\\twitter\\log.txt', debug_file_path='./logs\\twitter\\DEBUG_log.txt')],
        )

        # 開發用
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        DEV_PATH = os.path.join('decode_printer.txt')
        # 正式環境需讀取 000003_debin.log 檔案的內容

        # value re_Tweet_check 得到匹配到的轉推來源帳號 None代表沒有轉推
        with open(DEV_PATH, 'r', encoding='UTF-8', errors='ignore') as f:
            re_Tweet_check = f.read()

        re_Tweet_check = TwitterEntry_re_Tweet.entry_url_process(
            re_Tweet_check)  # 得到匹配到的轉推來源帳號或None等於非轉推

        # match is Twitter account or not
        match_output_tuple = TwitterAccountProcessor(
            str(DEV_PATH)
        ).process_twitter_account()
        """
        match_output_tuple = (
            True, '901Percent_', 'https://twitter.com/901Percent_/status/1788413030365282774', '1788413030365282774'
        )
        
        tuple(binary_search_result -> True, return value || twitter_link(Hardcode), twitter_post_id)
        """
        if match_output_tuple is None:
            SystemExit(0)
        else:
            return tuple(match_output_tuple), re_Tweet_check

    def process_twitter_account(self):

        match_output_tuple, re_Tweet_check = self.match_twitter_account()

        if re_Tweet_check == match_output_tuple[1] and re_Tweet_switch == True:
            print('\033[91mWarning: \033[33m\033[38;2;255;255;179m轉推阻擋已開啟，本次請求 \033[91m已阻擋 \033[33m'
                '\033[38;2;255;255;179m若要關閉\033[38;2;255;255;179m此功能在\033[0m'
                '\033[36m API_Twitter.py\033[91m \033[38;2;255;255;179m'
                '\033[0m將 \033[36mre_Tweet_switch\033[0m 變數設為\033[33m \033[36mFalse\033[0m')
            SystemExit(0)
        elif match_output_tuple is None:
            SystemExit(0)
        # match_output_tuple[0] is binary search bool
        elif bool(match_output_tuple[0]) is False:
            Error_Log_Handler.error_log()
            SystemExit(0)
        elif not match_output_tuple is False:
            # 網址哈希一下再存進去
            MD5 = hashlib.md5(
                str(match_output_tuple[2]).encode('utf-8')
            ).hexdigest()

            # 把 match Tag 轉成 str 後去除全部 ['()'] 字元
            Twitter_id = (
                str(match_output_tuple[1:-2])
                .replace("(", "").replace(")", "").replace("[", "")
                .replace("]", "").replace("'", "").replace(",", "")
            )

            # list(Twitter_cache_list)  ['qcpk0203','c682e42712551f88dfcefe076e2aeb93']
            self.Twitter_cache_list.append(Twitter_id)
            self.Twitter_cache_list.append(MD5)

            self._save_to_pkl_()

            Twitter.start_request(Twitter_id)  # 呼叫HTTP RSS請求和存入字典的操作
            TwitterMatcher().start_match() # 查找HashTag標籤並匹配IVE成員是誰或不只匹配到一人

    def _save_to_pkl_(self):
        # 開始存入 value 到 ../assets/Twitter_cache_dict.pkl
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(self.Twitter_cache_dict_pkl, 'rb') as file:
                existing_data = pickle.load(file)
        except FileNotFoundError:
            with open(self.Twitter_cache_dict_pkl, 'wb') as pkl:
                pickle.dump(list(self.Twitter_cache_list), pkl)
                existing_data = []
            logging.error(
                '  /assets/Twitter_cache_dict.pkl 遺失! 已經初始化，資料可能會產生異常'
            )

        # 將新的數據追加到現有數據中
        existing_data.append(self.Twitter_cache_list)
        
        # [['qcpk0203', 'c682e42712551f88dfcefe076e2aeb93']]
        # 將更新後的數據寫入文件
        with open(self.Twitter_cache_dict_pkl, 'wb') as file:
            pickle.dump(existing_data, file)


class TwitterEntry_re_Tweet:
    
    @staticmethod
    def entry_url_process(input_data):
        # 匹配 Twitter 轉推條目的 URL
        tw_regex = re.findall(
            r'https://twitter.com/.*?tweet\b', input_data, re.DOTALL)
        # 匹配轉推條目的 URL
        tw_regex_url = re.findall(
            r'https://twitter.com/(?:#1tweet|")', input_data)

        match_accounts = None
        try:
            for first_filter in tw_regex:
                # 如果匹配到的第一個 URL 不等於轉推條目的 URL
                if first_filter != tw_regex_url[0]:
                    # 將轉推條目的 URL 中的換行符替換為空白後進行過濾
                    filtered_entry = [re.sub(
                        r"(https?://[A-Za-z0-9./?=_:\-~]+)(?:[A-Za-z0-9./?=_:\-~]+)?$", '', first_filter.replace('\n', ''))]
                    # 在過濾後的條目中查找匹配的 Twitter 帳號
                    matches_data = [re.findall(
                        r"(?i)@([A-Za-z0-9_]{1,})", first_filter) for _ in filtered_entry]
                    # 將匹配到的 Twitter 帳號組合為一個字符串，如果未匹配到則返回 None
                    match_accounts = ' '.join(
                        [_[0] for _ in matches_data]) if matches_data else None
        except IndexError:
            match_accounts = None

        # 返回匹配到的轉推來源帳號或者返回 None
        return match_accounts


if __name__ == '__main__':
    API_Twitter().process_twitter_account()
