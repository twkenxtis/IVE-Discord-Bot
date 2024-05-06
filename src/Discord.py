import json
import logging
import os
import pickle
import urllib.parse

import discord
from discord.ext import commands


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


logging.basicConfig(
    level=logging.INFO,
    handlers=[ColoredLogHandler(
        fmt=logging.BASIC_FORMAT, file_path='./logs\\discord\\log.txt', debug_file_path='./logs\\discord\\DEBUG_log.txt')],
)


class Twitter_PKL_popup:
    def remove_first_values_from_twitter(count):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "../assets/Twitter_cache_dict.pkl"
        )

        if not os.path.exists(file_path):
            print("Error: File not found.")
            return
        try:
            with open(file_path, "rb") as f:
                loaded_list = pickle.load(f)
        except FileNotFoundError:
            print("Error: Unable to load data from file.")
            return
        if not loaded_list:
            print("List is empty now.")
            return
        if count > len(loaded_list):
            print(
                f"Error: List length ({len(loaded_list)}) is smaller than count ({count})."
            )
            return
        removed_values = []
        for _ in range(count):
            removed_values.append(loaded_list.pop(0))
        if len(loaded_list) == 1 and not loaded_list[0]:
            print("Only one empty list remaining. Deleting it.")
            loaded_list = []
        with open(file_path, "wb") as f:
            pickle.dump(loaded_list, f)


class IG_PKL_popup:
    def remove_first_values_from_ig(count):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "../assets/IG_cache_dict.pkl"
        )

        if not os.path.exists(file_path):
            print("Error: File not found.")
            return
        try:
            with open(file_path, "rb") as f:
                loaded_list = pickle.load(f)
        except FileNotFoundError:
            print("Error: Unable to load data from file.")
            return
        if not loaded_list:
            print("List is empty now.")
            return
        if count > len(loaded_list):
            print(
                f"Error: List length ({len(loaded_list)}) is smaller than count ({count})."
            )
            return
        removed_values = []
        for _ in range(count):
            removed_values.append(loaded_list.pop(0))
        if len(loaded_list) == 1 and not loaded_list[0]:
            print("Only one empty list remaining. Deleting it.")
            loaded_list = []
        with open(file_path, "wb") as f:
            pickle.dump(loaded_list, f)


class Twitter():
    def read_twitter_pkl():
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open('../assets/Twitter_cache_dict.pkl', 'rb') as pkl:
            twitter_rawpkl = pickle.load(pkl)
            return twitter_rawpkl

    def read_twitter_dict():
        with open('../assets/Twitter_dict.json', 'r') as file:
            twitter_dict = json.load(file)
            return twitter_dict


class Instagram:
    def read_ig_pkl():
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open('../assets/IG_cache_dict.pkl', 'rb') as pkl:
            ig_rawpkl = pickle.load(pkl)
            return ig_rawpkl

    def read_ig_dict():
        with open('../assets/IG_dict.json', 'r') as file:
            ig_dict = json.load(file)
            return ig_dict

    # 查解析後的路徑（parsed_url.path）是否以 "/p/" 開始

    def check_instagram_url(ig_url):
        parsed_url = urllib.parse.urlparse(ig_url)
        return parsed_url.path.startswith("/p/")


class Match_wich_account():
    def channel_id(self, ive_name):
        channel_id = {
            "GAEUL": "1237020442183860276",
            "fallingin__fall": "1237020442183860276",
            "YUJIN": "1237020290987458643",
            "_yujin_an": "1237020290987458643",
            "REI": "1237020461976522834",
            "reinyourheart": "1237020461976522834",
            "WONYOUNG": "1237020545527054346",
            "for_everyoung10": "1237020545527054346",
            "LIZ": "1237020520092794950",
            "liz.yeyo": "1237020520092794950",
            "LEESEO": "1237020484411985950",
            "eeseooes": "1237020484411985950"
        }

        found = False
        for key, value in channel_id.items():
            if ive_name == key:
                found = True
                return key, value
        if not found:
            return None, None

    def get_channel_id(self, ive_name):
        channel_key, channel_value = self.channel_id(ive_name)
        if channel_key is not None:
            return int(channel_value)
        else:
            logging.info("沒有匹配到的帳號")


class Discord_Twitter:
    def __init__(self):
        # 初始化工作目錄 環境變數
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.env_file_path = os.path.join('../config\\.env')
        # TODO: Development 開關用來判定要不要送出Discord訊息
        self.send_embed = True
        # 讀取.env 檔案內的 TOKEN 並設定給 bot
        self.TOKEN = self.get_env_var(self.env_file_path, 'TOKEN')
        # 主要功能是創建了一個Discord bot對象，並為其設置了命令前綴和意圖
        # 同時指定了當bot準備就緒時將調用相應的事件處理器方法
        self.bot = commands.Bot(
            command_prefix='%', intents=discord.Intents.all())
        self.bot.event(self.on_ready)

    # 抓環境檔案中指定變數的值，然後回傳該值
    def get_env_var(self, env_path, var_name):
        with open(env_path, 'r') as file:
            for line in file:
                if line.startswith(var_name):
                    value = line.split('=')[1].strip()
                    if value:  # check if value is not empty
                        return value
        logging.error(f'Discord TOKEN 無法在.env 辨識到，請檢察環境變數檔案')
        raise ValueError(
            f'Environment variable {var_name} not found in {env_path}')

    async def on_ready(self):
        print(f"目前登入身份 --> {self.bot.user}")

        # TODO: 這個 IF 判斷式開發完要刪除 僅用於開發測試使用！
        if self.send_embed:

            try:
                # Twitter 對應的 channel ID
                twitter_channel_id = Twitter.read_twitter_pkl()[0][1]
                channel_id = Match_wich_account().get_channel_id(twitter_channel_id)
            except IndexError:
                logging.info('No data in the twitter_cache.pkl')

            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="", color=discord.Color.purple())
            embed.set_author(
                name="🔗 七次撲空 ",
                icon_url="https://i.meee.com.tw/caHwoj6.png",
                url="https://twitter.com/qcpk0203/status/1787072894952255641"
            )

            embed.add_field(
                name="Title",
                value="貼文內容",
                inline=True,
            )

            urls = [

            ]

            for url in urls:
                await channel.send(url)
            DISCORD_send = await channel.send(embed=embed)

            if DISCORD_send:
                print('訊息已經成功發送!')

    def run(self):
        self.bot.run(self.TOKEN)


# 呼叫Discord bot running
Discord_Twitter().run()
