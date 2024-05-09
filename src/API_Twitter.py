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
            return match_output_tuple

    def process_twitter_account(self):
        match_output_tuple = self.match_twitter_account()

        if match_output_tuple is None and Error_Log_Handler.error_log() is None:
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

            Twitter.twitter_rss(Twitter_id)  # 呼叫HTTP RSS請求和存入字典的操作

    def _save_to_pkl_(self):
        # 開始存入 value 到 ../assets/Twitter_cache_dict.pkl
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(self.Twitter_cache_dict_pkl, 'rb') as file:
                existing_data = pickle.load(file)
        except FileNotFoundError:
            with open(self.Twitter_cache_dict_pkl, 'wb') as pkl:
                pickle.dump(list(self.Twitter_cache_list), pkl)
                existing_data = ''
            logging.warning(
                '  /assets/Twitter_cache_dict.pkl 遺失! 已經初始化，程式可能會產生異常'
            )

        # 將新的數據追加到現有數據中
        existing_data.append(self.Twitter_cache_list)

        # 將更新後的數據寫入文件
        with open(self.Twitter_cache_dict_pkl, 'wb') as file:
            pickle.dump(existing_data, file)


if __name__ == '__main__':
    API_Twitter().process_twitter_account()
