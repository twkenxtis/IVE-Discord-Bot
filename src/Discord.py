import asyncio
import json
import logging
import os
import pickle
import urllib.parse
from datetime import datetime

################################################
# discord python power by Rapptz MIT License
# https://github.com/Rapptz/discord.py
################################################
import discord
from discord.ext import commands
from discord import Embed


class ColoredLogHandler(logging.StreamHandler):
    def __init__(self, fmt=None, file_path=None, debug_file_path=None):
        # 呼叫父類別的建構函數
        super().__init__()

        # 定義不同等級的顏色映射
        self.color_mapping = {
            logging.DEBUG: '\033[92m',           # 淺綠色
            logging.INFO: '\033[96m',            # 青色
            logging.WARNING: '\033[38;5;214m',   # 金黃色
            logging.ERROR: '\x1b[31m',           # 深紅色
            logging.CRITICAL:  '\033[91m',      # 深紫紅色
        }
        self.reset_color = '\033[0m'  # 重置顏色
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
        # 將日誌訊息輸出到控製臺
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


class TimeDifferenceCalculator:

    def __init__(self):
        pass

    @staticmethod
    def calculate_time_difference(target_time_str):
        # 將目標時間字符串轉換為 datetime 對象
        target_time = datetime.strptime(target_time_str, "%Y/%m/%d %H:%M:%S")
        # 獲取當前時間
        current_time = datetime.now()
        # 計算時間差
        time_difference = current_time - target_time
        # 將時間差轉換為秒
        time_difference_seconds = time_difference.total_seconds()
        return time_difference_seconds

    @staticmethod
    def main(input_time_cal):
        # 格式為 "YYYY/MM/DD HH:MM:SS"
        time_difference_seconds = TimeDifferenceCalculator.calculate_time_difference(
            input_time_cal)
        return float(time_difference_seconds)


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
            "REI": "1238508631876567120",
            "reinyourheart": "1238508631876567120",
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
            # logging.info("沒有匹配到的帳號")
            pass


class ButtonView(discord.ui.View):
    def __init__(self, url: str, timeout: float | None = 60):
        super().__init__(timeout=timeout)

        url_button = discord.ui.Button(
            label="View on X",
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
file_path_PKL = '../assets/Twitter_cache_dict.pkl'


def format_urls(url_string):
    url_list = url_string.split(" ")
    formatted_urls = [
        f"[{index+1}]({url})" for index, url in enumerate(url_list)]
    return ' '.join(formatted_urls)


def discord_twitter():
    global TOKEN

    async def send_discord_message(channel, ive_members, embed, button_view, twitter_id, formatted_urls_str, time_offset):
        if time_offset < 1.5 and channel is not None:
            dc_message = await channel.send(str(formatted_urls_str))
            dc_embed = await channel.send(embed=embed, view=button_view)
            if dc_message and dc_embed:
                Twitter_PKL_popup.remove_first_values_from_twitter(2)
                print(
                    f'發送到 {ive_members} 頻道 / Twitter帳號: {twitter_id} / OK，PKL Cache 已經清除')
            else:
                logging.critical('Discord 消息發送失敗')
        else:
            Twitter_PKL_popup.remove_first_values_from_twitter(2)
            logging.info('DC 無法發送訊息，該訊息非IVE貼文或已經發過，準備清除PKL快取資料...')

    async def check_file_and_trigger_send_embed():
        PKL_READ = False
        print(
            '\033[38;2;255;179;255mKeeping detecting Twitter_cache_dict.pkl length...\033[m')

        while True:
            if os.path.exists(file_path_PKL):
                with open(file_path_PKL, 'rb') as pkl:
                    pkl_data = pickle.load(pkl)
                    if len(pkl_data) >= 2 and pkl_data[1] is not None:
                        print(
                            f"\033[38;2;204;0;102m檢測新訊息 \033[0m{datetime.now()}  \033[38;2;102;140;255m{pkl_data}\033[0m")
                        PKL_READ = True
                        await send_embed(PKL_READ)
                    elif len(pkl_data) >= 2 and pkl_data[1] is None:
                        print(
                            f"\033[38;2;204;0;102m檢測新訊息 \033[0m{datetime.now()}  \033[38;2;102;140;255m{pkl_data}\033[0m")
                        Twitter_PKL_popup.remove_first_values_from_twitter(2)
                        logging.info('此貼文沒有符合的#IVE Tag，已清除PKL快取資料...')
            else:
                logging.error(
                    "Discord.py fail to read Twitter_cache_dict.pkl data")
                raise Exception(FileNotFoundError(
                    f"PKL檔案不存在: {file_path_PKL}"))

            await asyncio.sleep(1)

    @ client.event
    async def on_ready():
        print(f"目前登入身份 --> {client.user}")
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Accendio"))
        await check_file_and_trigger_send_embed()

    @ client.event
    async def send_embed(PKL_READ: bool):
        # 讀取 Twitter_cache_dict.pkl
        if PKL_READ is True:
            ive_members = Twitter.read_twitter_pkl()[1][0]  # REI or GROUPS
            MD5 = Twitter.read_twitter_pkl()[0][1]  # 字典的Key

            channel_id = Match_wich_account().get_channel_id(str(ive_members))
            minive_link = Match_wich_minive().get_minive_link(str(ive_members))

            key = MD5
            if key in Twitter.read_twitter_dict():
                value = Twitter.read_twitter_dict()[key]
                twitter_author = value[0]  # 七次撲空
                # https://twitter.com/qcpk0203/status/1784927109426933969
                twitter_link = value[1]
                # qcpk0203 slice[20:27]是因為網址是固定的長度
                twitter_id = value[1][20:27]
                twitter_entry = value[2]  # Twitter 貼文內容
                post_time = value[3]  # 2024/04/29 20:45:59 (貼文發布時間)
                # 2024/05/10 20:08:07 (存入資料時系統時間)
                sys_time_from_dict = value[4]
                img_count = value[5]  # int 照片數量
                twitter_all_img = value[6]  # 所有的照片網址
                author_avatar = value[7]  # 貼文作者的頭像網址

                time_offset = TimeDifferenceCalculator.main(sys_time_from_dict)
                channel = client.get_channel(channel_id)

                embed = discord.Embed(
                    title=twitter_author, url=twitter_link, color=0xed68a6)
                embed.set_author(
                    name='New post from  ' + '(@' + str(twitter_id) + ')',
                    icon_url=minive_link,
                    # url=twitter_link
                )
                embed.add_field(
                    name='　',
                    value=twitter_entry,
                    inline=True,
                )
                embed.set_thumbnail(url=author_avatar)
                post_time_obj = datetime.strptime(
                    post_time, '%Y/%m/%d %H:%M:%S')
                embed.set_footer(text='MIT © 2024 omenbibi   ' + '🖼️ ' + str(img_count),
                                 icon_url='https://i.meee.com.tw/caHwoj6.png')
                embed.timestamp = post_time_obj
                button_url = twitter_link
                button_view = ButtonView(url=button_url)

                formatted_urls_str = format_urls(twitter_all_img)
                await send_discord_message(channel, ive_members, embed, button_view, twitter_id, formatted_urls_str, time_offset)
        else:
            logging.WARNING('請檢查PKL 快取資料，該狀態不應該被觸發Discord EMBED 物件')
            raise Exception('PKL 快取資料異常')

    client.run(TOKEN)


if __name__ == "__main__":
    discord_twitter()
