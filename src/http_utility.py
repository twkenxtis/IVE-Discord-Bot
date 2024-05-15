import logging
import random
import time
import requests
from datetime import datetime

from fake_useragent import UserAgent
from timezone import SystemTime
from custom_log import ColoredLogHandler

logging.basicConfig(level=logging.INFO, handlers=[ColoredLogHandler()])


class HttpRequester:

    def __init__(self, url):
        self.url = url
        self.response_content = None

    def send_request(self):
        response = requests.get(self.url, timeout=10)
        self.response_content = response.text

    def get_response_content(self):
        return str(self.response_content)

    def start_requests(self):
        ua = UserAgent()
        headers = {"user-agent": ua.random}
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(
                    f"\033[38;2;102;153;153mSystem current time: {SystemTime.format_current_time()}\033[0m")
                self.response_content = response.text
                logging.info(
                    f" {self.url} code: {response.status_code}")
                return response.status_code
            else:
                print(
                    f"\033[38;2;102;153;153mSystem current time: {SystemTime.format_current_time()}\033[0m")
                self.response_content = response.text
                logging.warning(
                    f" {self.url} code: {response.status_code}")
                return None

        except TimeoutError as e:
            print(
                f"\033[38;2;102;153;153mSystem current time: {SystemTime.format_current_time()}\033[0m")
            logging.error(
                f"{self.url} Timeout Error: {str(e)}"
            )
            return None
        except Exception as e:
            print(
                f"\033[38;2;102;153;153mSystem current time: {SystemTime.format_current_time()}\033[0m")
            logging.error(
                f"{self.url} Unexpected error: {str(e)}"
            )
            return None
