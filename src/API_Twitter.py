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

# 是否開啟轉推阻擋功能 Default: False
re_Tweet_switch = True


class API_Twitter:

    def __init__(self):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        self.Twitter_cache_list = []
        self.Twitter_cache_dict_pkl = os.path.join(
            parent_dir, "assets", "Twitter_cache_dict.pkl"
        )
        self.Twitter_dict_json = os.path.join(
            parent_dir, "assets", "Twitter_dict.json"
        )

        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                ColoredLogHandler(
                    fmt=logging.BASIC_FORMAT)
            ]
        )

    def match_twitter_account(self, input_notify: str):

        re_Tweet_check = None

        re_Tweet_check = TwitterEntry_re_Tweet.entry_url_process(
            input_notify
        )  # 得到匹配到的轉推 str=來源帳號 或 None=非轉推

        # match is Twitter account or not
        match_output_tuple = TwitterAccountProcessor(
            str(input_notify)
        ).process_twitter_account()
        """
        match_output_tuple = (
            True, '901Percent_', 'https://twitter.com/901Percent_/status/1788413030365282774', '1788413030365282774'
        )
        
        tuple(binary_search_result -> True, return value || twitter_link(Hardcode), twitter_post_id)
        """

        print('\033[95mthis is match output and re_Tweet_cheek:\033[0m')
        print(type(match_output_tuple), type(re_Tweet_check))
        print(match_output_tuple, re_Tweet_check)

        if match_output_tuple is None:
            re_Tweet_check = None
            match_output_tuple = None
            pass
        else:
            print('\033[92mAPI_Twitter 開始運作!\033[0m')
            return tuple(match_output_tuple), re_Tweet_check

    def process_twitter_account(self, input_notify):

        result_tuple = self.match_twitter_account(input_notify)

        if result_tuple is None:
            re_Tweet_check = None
            match_output_tuple = None
            Error_Log_Handler.error_log()
        else:
            match_output_tuple, re_Tweet_check = self.match_twitter_account(
                input_notify)

            # 轉推判斷
            if re_Tweet_check == match_output_tuple[1] and re_Tweet_switch == True:
                print(
                    "\033[91mWarning: \033[33m\033[38;2;255;255;179m轉推阻擋已開啟，本次請求 \033[91m已阻擋 \033[33m"
                    "\033[38;2;255;255;179m若要關閉\033[38;2;255;255;179m此功能在\033[0m"
                    "\033[36m API_Twitter.py\033[91m \033[38;2;255;255;179m"
                    "\033[0m將 \033[36mre_Tweet_switch\033[0m 變數設為\033[33m \033[36mFalse\033[0m"
                )
            else:
                # match_output_tuple[0] is binary search bool
                if bool(match_output_tuple[0]) is False:
                    Error_Log_Handler.error_log()
                elif not match_output_tuple is False:
                    self.process_valid_tweet(match_output_tuple)

    def process_valid_tweet(self, match_output_tuple):

        # 網址哈希一下再存進去
        MD5 = hashlib.md5(
            str(match_output_tuple[2]).encode("utf-8")).hexdigest()

        # 把 match Tag 轉成 str 後去除全部 ['()'] 字元
        Twitter_id = (
            str(match_output_tuple[1:-2])
            .replace("(", "")
            .replace(")", "")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace(",", "")
        )

        # list(Twitter_cache_list)  ['qcpk0203','c682e42712551f88dfcefe076e2aeb93']
        self.Twitter_cache_list.append(Twitter_id)
        self.Twitter_cache_list.append(MD5)

        print('帳號:', Twitter_id)

        is_in_Dict = Key_Exists_in_Dict().dict_key_found(MD5)

        if int(is_in_Dict) == 1:
            logging.info("此通知已經存在資料庫中，不再新增")
        elif int(is_in_Dict) == 0:
            self.__save_to_pkl_()  # 以List存入['Twitter_id, MD5']

            Twitter().start_request(Twitter_id)  # 呼叫HTTP RSS請求和存入字典的操作
            TwitterMatcher().start_match()  # 查找HashTag標籤並匹配IVE成員是誰或不只匹配到一人

    # 私有方法
    def __save_to_pkl_(self):

        # 開始存入 value 到 ../assets/Twitter_cache_dict.pkl
        try:
            with open(self.Twitter_cache_dict_pkl, "rb") as file:
                existing_data = pickle.load(file)
        except FileNotFoundError:
            with open(self.Twitter_cache_dict_pkl, "wb") as pkl:
                pickle.dump(list(self.Twitter_cache_list), pkl)
                existing_data = []
            logging.error(
                "  /assets/Twitter_cache_dict.pkl 遺失! 已經初始化，資料可能會產生異常"
            )

        # 將新的數據追加到現有數據中
        existing_data.append(self.Twitter_cache_list)

        print('\033[9;33;40mAPI_Twitter_PKL 路徑:\033[0m',
              self.Twitter_cache_dict_pkl)

        # [['qcpk0203', 'c682e42712551f88dfcefe076e2aeb93']]
        # 將更新後的數據寫入文件
        with open(self.Twitter_cache_dict_pkl, "wb") as file:
            pickle.dump(existing_data, file)


class TwitterEntry_re_Tweet:

    @staticmethod
    def entry_url_process(input_data):
        # 匹配 Twitter 轉推條目的 URL
        tw_regex = re.findall(
            r"https://twitter.com/.*?tweet\b", input_data, re.DOTALL)
        # 匹配轉推條目的 URL
        tw_regex_url = re.findall(
            r'https://twitter.com/(?:#1tweet|")', input_data)

        match_accounts = None
        try:
            for first_filter in tw_regex:

                # 如果匹配到的第一個 URL 不等於轉推條目的 URL
                if first_filter != tw_regex_url[0]:

                    # 將轉推條目的 URL 中的換行符替換為空白後進行過濾
                    filtered_entry = [
                        re.sub(
                            r"(https?://[A-Za-z0-9./?=_:\-~]+)(?:[A-Za-z0-9./?=_:\-~]+)?$",
                            "",
                            first_filter.replace("\n", ""),
                        )
                    ]

                    # 在過濾後的條目中查找匹配的 Twitter 帳號
                    matches_data = [
                        re.findall(r"(?i)@([A-Za-z0-9_]{1,})", first_filter)
                        for _ in filtered_entry
                    ]

                    # 將匹配到的 Twitter 帳號組合為一個字符串，如果未匹配到則返回 None
                    match_accounts = (
                        " ".join([_[0] for _ in matches_data]
                                 ) if matches_data else None
                    )
        except IndexError:
            match_accounts = None
        # 返回匹配到的轉推來源帳號或者返回 None
        return match_accounts


class Key_Exists_in_Dict:

    def read_twitter_dict(self):

        # 獲取當前檔案所在的目錄路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(
            current_dir,  "..", "assets", "Twitter_dict.json")

        file_path = os.path.abspath(file_path)

        print("\n\033[9;33;40m路徑追蹤\033[0m" +
              'class Key_Exists_in_Dict ', file_path)

        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                twitter_dict = json.load(f)
                return twitter_dict
        else:
            with open(file_path, "w") as f:
                json.dump({}, f)
            with open(file_path, "r") as f:
                twitter_dict = json.load(f)
                logging.warning(
                    " 檢測到Twitter_ditct.json異常，已初始化 /assets/Twitter_dict.json ，結果可能不準確!"
                )
                return twitter_dict

    def dict_key_found(self, MD5):
        twitter_dict = self.read_twitter_dict()

        if MD5 and twitter_dict is not None:
            if MD5 in twitter_dict:
                return int(1)  # FOUND
            else:
                return int(0)  # NOT FOUND
