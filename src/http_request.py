import logging
import random
import time
from datetime import datetime

import httpx
from fake_useragent import UserAgent

from timezone import SystemTime


class ColoredLogHandler(logging.StreamHandler):
    def __init__(self, fmt=None):
        super().__init__()
        # 定義不同等級的顏色映射
        self.color_mapping = {
            logging.DEBUG:'\033[92m',           # 浅绿色
            logging.INFO:'\033[96m',            # 青色
            logging.WARNING:'\033[38;5;214m',   # 金黃色
            logging.ERROR:'\x1b[31m',           # 深红色
            logging.CRITICAL:  '\033[91m',      # 深紫红色
                                   
            
        }
        self.reset_color = '\033[0m'  # 重置颜色
        self._fmt = fmt or logging.BASIC_FORMAT

    def format(self, record):
        # 取得日誌訊息的顏色格式
        color_format = f"{self.color_mapping.get(record.levelno, '')}{self._fmt}{self.reset_color}"
        formatter = logging.Formatter(color_format)
        return formatter.format(record)


class HTTP3Requester:
    def __init__(self, url):
        logging.basicConfig(level=logging.INFO, handlers=[ColoredLogHandler()])
        self.url = url
        # response_content屬性，用於保存回應的內容
        self.response_content = None

    # 使用httpx庫的Client類別來發送同步的GET請求
    # 使用self.url屬性作為請求的URL，並將回應的內容保存到self.response_content屬性中
    def send_request(self):
        with httpx.Client() as client:
            response = client.get(self.url, timeout=5)
            self.response_content = response.text  # STR 

    # 定義了一個get_response_content方法，用於獲取self.response_content屬性的值並返回
    def get_response_content(self):
        return self.response_content

    def make_request(self):
        # 在這個方法中，使用了UserAgent類別生成一個隨機的使用者代理(User Agent)
        ua = UserAgent()
        # 創建了一個包含隨機使用者代理的標頭(headers)字典
        headers = {"user-agent": ua.random}
        # 使用httpx庫的Client類別來發送同步的GET請求。
        with httpx.Client() as client:
            try:
                response = client.get(self.url, headers=headers, timeout=10)
                if response is not None and 200 == response.status_code:
                    self.response_content = response.text  # string response content
                    print(
                        # system current time
                        f"\033[90m{SystemTime.format_current_time()}\033[0m "
                        # http response code
                        f"\033[38;2;255;212;128mhttp response code:\033[0m \033[38;2;153;255;214m{response.status_code}\033[0m "
                    )
            except Exception as HTTP_ERROR_EXCEPTION:
                print(
                    # system current time
                    f"System current time: \033[90m{SystemTime.format_current_time()}\033[0m "
                    # error message
                    f"\033[91mError: {str(HTTP_ERROR_EXCEPTION)}\033[0m"
                    )
            return self.response_content

    def start_requests(self, num_of_requests):
        if num_of_requests > 1:
            print(
                f"\033[91m Requests: \033[0m\033[38;5;118m{num_of_requests}\033[0m \033[38;2;255;212;128m > 1 Enable waiting time...\033[0m")
            for _ in range(num_of_requests):
                # 使用同步的 time.sleep() 來實現等待
                sleep_time = random.randint(13, 29)  # SLEEP TIME CHANGE
                time.sleep(sleep_time)

                self.make_request()

                print(f"\033[90m{SystemTime.format_current_time()}\033[0m "  # system current time
                      f"\033[91m Waiting \033[0m \033[38;5;208m{sleep_time}s\033[0m \033[38;2;255;212;128m for request...\033[0m")
        else:
            # 調用 make_request 方法 第一個請求不受 sleep_time 的限製
            self.make_request()
