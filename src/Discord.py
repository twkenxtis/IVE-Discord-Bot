import os
import asyncio
import pickle
import datetime

import json
import logging
import urllib.parse

import discord
from discord.ext import commands
from discord import Embed


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
            "eeseooes": "1237020484411985950",
            "GROUPS": "1237421929229582439"
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


class Match_wich_minive():
    def minive_id(self, ive_name):
        minive_link = {
            "GAEUL": "https://cdn.discordapp.com/emojis/1181917701568995328.webp?size=96&quality=lossless",
            "fallingin__fall": "https://cdn.discordapp.com/emojis/1181917701568995328.webp?size=96&quality=lossless",
            "YUJIN": "https://cdn.discordapp.com/emojis/1181917638578941962.webp?size=96&quality=lossless",
            "_yujin_an": "https://cdn.discordapp.com/emojis/1181917638578941962.webp?size=96&quality=lossless",
            "REI": "https://cdn.discordapp.com/emojis/1181917769256677426.webp?size=96&quality=lossless",
            "reinyourheart": "https://cdn.discordapp.com/emojis/1181917769256677426.webp?size=96&quality=lossless",
            "WONYOUNG": "https://cdn.discordapp.com/emojis/1181917841109307423.webp?size=96&quality=lossless",
            "for_everyoung10": "https://cdn.discordapp.com/emojis/1181917841109307423.webp?size=96&quality=lossless",
            "LIZ": "https://cdn.discordapp.com/emojis/1181917474581651567.webp?size=96&quality=lossless",
            "liz.yeyo": "https://cdn.discordapp.com/emojis/1181917474581651567.webp?size=96&quality=lossless",
            "LEESEO": "https://cdn.discordapp.com/emojis/1181917554948722810.webp?size=96&quality=lossless",
            "eeseooes": "https://cdn.discordapp.com/emojis/1181917554948722810.webp?size=96&quality=lossless",
            "GROUPS": "https://cdn.discordapp.com/emojis/1142897969876701395.webp?size=96&quality=lossless"
        }

        found = False
        for key, value in minive_link.items():
            if ive_name == key:
                found = True
                return key, value
        if not found:
            return None, None

    def get_minive_link(self, ive_name):
        minive_key, minive_value = self.minive_id(ive_name)
        if minive_key is not None:
            return str(minive_value)
        else:
            logging.info("沒有匹配到的帳號")


class ButtonView(discord.ui.View):
    def __init__(self, url: str, timeout: float | None = 60):
        super().__init__(timeout=timeout)

        url_button = discord.ui.Button(
            label="Link",
            style=discord.ButtonStyle.link,
            url=url
        )
        self.add_item(url_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author


def load_DC_token():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(script_dir, '../config/.env')
    with open(env_file_path, 'r') as file:
        for line in file:
            if line.startswith('TOKEN'):
                return line.split('=')[1].strip()


TOKEN = load_DC_token()

intents = discord.Intents.default()
intents.message_content = True
# 前綴設定為None，不使用預設的 !
client = commands.Bot(command_prefix=None, intents=intents)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
file_path_cache = '../assets/Twitter_cache_dict.pkl'


def discord_twitter():

    global TOKEN

    async def check_file_and_trigger_send_embed():
        print(
            '\033[38;2;255;179;255mKeeping detecting Twitter_cache_dict.pkl length...\033[m')
        while True:
            if os.path.exists(file_path_cache):
                with open(file_path_cache, 'rb') as pkl:
                    data = pickle.load(pkl)
                    if len(data) >= 1:
                        print(f"{datetime.datetime.now()} - Data: {data}")
                        await asyncio.sleep(1)
                        await send_embed()

            await asyncio.sleep(0.5)

    @client.event
    async def on_ready():
        print(f"目前登入身份 --> {client.user}")
        await check_file_and_trigger_send_embed()

    @client.event
    async def send_embed():
        try:
            # Twitter 對應的 channel ID
            twitter_channel_id = Twitter.read_twitter_pkl()[0][1]
            twitter_id = Twitter.read_twitter_pkl()[0][0]
            channel_id = Match_wich_account().get_channel_id(twitter_channel_id)
            minive_link = Match_wich_minive().get_minive_link(str(twitter_channel_id))

            key_to_search = Twitter.read_twitter_pkl()[0][2]
            if key_to_search in Twitter.read_twitter_dict():
                value = Twitter.read_twitter_dict()[key_to_search]
                twitter_author = value[0]
                twitter_link = value[1]
                twitter_entry = value[2]
                post_time = value[3]
                img_count = value[5]
                twitter_all_img = value[6]
        except IndexError:
            logging.error('No data in the twitter_cache.pkl')

        channel = client.get_channel(channel_id)

        embed = discord.Embed(title="", color=discord.Color.purple())
        embed.set_author(
            name=twitter_author + '   ' +
            '@(' + str(twitter_id) + ') ',
            icon_url="https://i.meee.com.tw/caHwoj6.png",
            url=twitter_link
        )

        embed.add_field(
            name='',
            value=twitter_entry,
            inline=True,
        )

        embed.set_footer(text='' + post_time +
                         '   🖼️ ' + str(img_count),
                         icon_url=str(minive_link))

        def format_urls(url_string):
            url_list = url_string.split(" ")
            formatted_urls = []
            for index, url in enumerate(url_list):
                markdown_url = f"[{index+1}]({url})"
                formatted_urls.append(markdown_url)
            formatted_urls_str = ' '.join(formatted_urls)
            return formatted_urls_str

        formatted_urls_str = format_urls(twitter_all_img)
        await channel.send(str(formatted_urls_str))

        button_url = twitter_link

        button_view = ButtonView(url=button_url)

        DISCORD_send = await channel.send(embed=embed, view=button_view)

        if DISCORD_send:
            Twitter_PKL_popup.remove_first_values_from_twitter(1)
            print('\x1b[38;2;255;255;51m發送到　\x1b[0m' + twitter_channel_id + ' ' +
                  twitter_id + '　\x1b[91mOK，PKL Cache已經清除\x1b[0m')
        else:
            print('Discord 消息發送失敗')
            logging.error('Discord 消息發送失敗')

    client.run(TOKEN)


if __name__ == "__main__":
    discord_twitter()
