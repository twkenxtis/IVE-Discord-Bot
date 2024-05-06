import logging
import re
import urllib.parse


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


class InstagramFilter:

    logging.basicConfig(
        level=logging.INFO,
        handlers=[ColoredLogHandler(
            fmt=logging.BASIC_FORMAT, file_path='./logs\\instagram\\log.txt', debug_file_path='./logs\\instagram\\DEBUG_log.txt')],
    )

    input_IG_notify_data = ['']

    @staticmethod
    def main():
        if InstagramFilter.input_IG_notify_data is not None:
            # 使用正則表達式匹配 input_IG_notify_data 中的 Instagram 網址
            url_regex = re.findall(
                r'https://www.instagram.com/p/.*?\?utm_source=web_push_encrypted&ndid=.*?(?=\s|$)', InstagramFilter.input_IG_notify_data)
        else:
            logging.error("Input data is None. Please check the input data.")

        for ig_links in url_regex:

            # 將 Instagram 網址轉換為可讀取的格式
            ig_filtered_links = ' '.join(
                InstagramFilter.find_instagram_links(ig_links))
            # 從網址中提取文章 ID
            ig_post_id = InstagramFilter.extract_post_id_from_url(
                ig_filtered_links)

            # print(ig_filtered_links) # Output https://www.instagram.com/p/C6IFfwCh-kB
            # print(ig_post_id)  # Output C6IFfwCh-kB
            end_data = f"LINK-> {ig_filtered_links}｜ID-> {ig_post_id}"
            logging.info(end_data)

            return ig_filtered_links, ig_post_id

    @staticmethod
    def find_instagram_links(input_IG_notify_data):
        # Create an empty list to store the Instagram links
        instagram_links = []

        # 用雙引號 (") 分割輸入字符串，提取 URL
        for _ in input_IG_notify_data.split('"'):

            # Search for URLs that match the Instagram pattern
            match = re.search(r'https://www.instagram.com/p/[a-zA-Z0-9_-]+', _)

            # Extract the Instagram link and append it to the list if a match is found
            match_ig_links = match.group(0) if match else None
            if match_ig_links:
                instagram_links.append(match_ig_links)
        # Return the list of Instagram links
        return instagram_links

    @staticmethod
    def extract_post_id_from_url(input_IG_notify_data):
        # 使用 urllib.parse 解析 URL
        parsed_url = urllib.parse.urlparse(input_IG_notify_data)

        # 從解析後的 URL 中獲取"路徑"部分
        path_url = urllib.parse.unquote(parsed_url.path)

        # 將URL路徑部分 分割成多個部分，並取最後一個部分作為 post_id
        url_end_parts = path_url.split("/")
        post_id = url_end_parts[-1]
        return post_id
