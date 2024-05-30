# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import asyncio
import logging
import os
import pickle
import re
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from functools import lru_cache

from cache import cache_manager
from custom_log import logger_API__Discord
from timezone import get_formatted_current_time

import discord
from discord.ext import commands
# discord is used under the MIT License
# Copyright (c) 2015-present Rapptz
# For more details, see the LICENSE file included with the distribution
from loguru import logger
# loguru is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution


logging.basicConfig(level=logging.INFO)


class DCBot_Twitter(object):

    @staticmethod
    @ lru_cache(maxsize=None)
    def load_pickle_dict() -> dict:
        # 獲取pkl文件的絕對路徑
        pkl_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         "..", "assets", "Twitter_dict.pkl")
        )
        if not os.path.isfile(pkl_file):
            # 若文件不存在，通過日誌記錄錯誤信息並拋出FileNotFoundError
            logger.error(f"pkl_file: {pkl_file} 文件不存在")
            raise FileNotFoundError(f"pkl_file: {pkl_file} 文件不存在，請確認路徑是否正確")

        with open(pkl_file, "rb") as pkl:
            # 使用pickle的loads方法加載pkl文件，fix_imports=True表示兼容python2的導入方式
            pkl_data = pickle.loads(pkl.read(), fix_imports=True)
            return pkl_data

    @staticmethod
    # 定義一個用於並發加載數據的靜態方法，返回字典類型的數據
    def load_data_concurrently() -> dict:
        try:
            # 使用ProcessPoolExecutor創建進程池進行並發執行
            with ProcessPoolExecutor() as executor:
                # 提交load_pickle_dict方法至進程池執行，並使用result()等待結果返回
                return executor.submit(DCBot_Twitter.load_pickle_dict).result()
        except UnboundLocalError:
            raise
        except FileNotFoundError:
            raise
        except EOFError:
            # 若讀寫 IO 打架就 1 秒無限重試
            time.sleep(1)
            DCBot_Twitter.load_data_concurrently()

    @staticmethod
    def load_DC_token():
        def recursive_search(lines: list[str]) -> str:
            if not lines:
                logger.critical("無法於環境變數文件找到 Discord_TOKEN 值")
                raise ValueError("請確認.env文件是否包含 Discord_TOKEN 欄位")

            # 每次只判斷傳遞的第一行，去除空格
            match [lines[0].strip()]:
                # 判斷清單中的第一個元素是否為 Discord_TOKEN 開頭
                case [value] if value.startswith('Discord_TOKEN'):
                    # 記得要去掉前後的空白字元防止錯誤
                    # 用字串方法處理值，返回第一個匹配值給 value token
                    token = value.split('=', 1)[1].strip()
                    # 假設 Discord token 長度至少為 72
                    if len(token) >= 72:
                        return token
                    else:
                        logger.critical("Discord_TOKEN 長度小於 72")
                        raise ValueError("Discord_TOKEN 長度不足 72")
                case _:
                    # 遞迴調用傳入值，字串方法每次檢查一行，直到沒有值
                    return recursive_search(lines[1:])

        try:
            # 獲取當前腳本所在目錄的絕對路徑
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # 打開.env文件作為讀取模式
            with open(os.path.join(script_dir, '..', 'config', '.env'), 'r') as env_file:
                # 使用 readlines() 函式逐行讀取文件中的內容，並將其傳遞給遞迴函式 recursive_search
                return recursive_search(env_file.readlines())
        # 如果文件未找到，捕獲 FileNotFoundError 並拋出錯誤消息
        except FileNotFoundError:
            logger.error("找不到.env文件，請重新建立環境變數檔案")
            raise FileNotFoundError("找不到.env文件，請重新建立環境變數檔案")

    @ lru_cache(maxsize=12)
    def get_minive_link(ive_name: str) -> str:
        minive_link = {
            "GAEUL": "https://i.imgur.com/UiEwQ7l.png",
            "fallingin__fall": "https://i.imgur.com/UiEwQ7l.png",
            "YUJIN": "https://i.imgur.com/d4KBTtz.png",
            "_yujin_an": "https://i.imgur.com/d4KBTtz.png",
            "REI": "https://i.imgur.com/sUpaBon.png",
            "reinyourheart": "https://i.imgur.com/sUpaBon.png",
            "WONYOUNG": "https://i.imgur.com/59R7HpU.png",
            "for_everyoung10": "https://i.imgur.com/59R7HpU.png",
            "LIZ": "https://i.imgur.com/kjxBjbj.png",
            "liz.yeyo": "https://i.imgur.com/kjxBjbj.png",
            "LEESEO": "https://i.imgur.com/eBFe7Ge.png",
            "eeseooes": "https://i.imgur.com/eBFe7Ge.png",
            "GROUPS": "https://i.imgur.com/WnkrrJS.png",
            "IVE_Only": "https://i.imgur.com/WnkrrJS.png"
        }

        # 因為 'async def send_embed' 會確保只有正確的傳入值所以不捕捉錯誤，直接 return value
        return minive_link.get(ive_name)

    @staticmethod
    @ lru_cache(maxsize=9)
    def channel_id(ive_name: str) -> int:
        channel_dict = {
            "GAEUL": "1142900837300043889",
            "fallingin__fall": "1142900837300043889",
            "YUJIN": "1142900711315734599",
            "_yujin_an": "1142900711315734599",
            "REI": "1142900891393994782",
            "reinyourheart": "1142900891393994782",
            "WONYOUNG": "1142900973405229056",
            "for_everyoung10": "1142900973405229056",
            "LIZ": "1142901102526869556",
            "liz.yeyo": "1142901102526869556",
            "LEESEO": "1142901201332097205",
            "eeseooes": "1142901201332097205",
            "GROUPS": "1157550597248135208",
            "IVE_Only": "1142905266703192157"

        }
        # 因為 'async def send_embed' 會確保只有正確的傳入值所以不捕捉錯誤，直接 return value
        # 注意 return 值為字串，所以要用 str() 轉換成 int 類型，不然 Discord API 會拒絕並報錯
        return int(channel_dict.get(ive_name))


class ButtonView(discord.ui.View):
    def __init__(self, url: str, timeout: float | None = 60):
        # 初始化函數，設置超時時間
        super().__init__(timeout=timeout)

        # 創建一個連結按鈕
        url_button = discord.ui.Button(
            label="在推特上查看",
            # 按鈕樣式為連結
            style=discord.ButtonStyle.link,
            # 按鈕連結的URL
            url=url
        )
        self.add_item(url_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # 互動檢查函數，確保只有特定用戶可以與按鈕互動
        return interaction.user == self.ctx.author  # 返回互動用戶是否為上下文作者


# Discord bot 全局設定
# https://discordpy.readthedocs.io/en/stable/intro.html
intents = discord.Intents.default()
intents.message_content = True
# 前綴設定
client = commands.Bot(command_prefix='!!', intents=intents)


def discord_twitter():

    # 接收格式化好的 Value 並發送Discord訊息函式
    async def send_discord_message(channel, ive_members, embed, button_view,
                                   twitter_id, twitter_all_img, MD5, img_count,
                                   twitter_entry):
        """
        cache_manager(object).dc_cache(fun) 用來儲存已發送過的訊息MD5值
        並對字典以更新的方式寫入 "SENDED" 值，以便Discord.py 識別訊息是否已經被發送過
        詳細工作流程請參考 cache.py
        """
        cache_manager.dc_cache(MD5)

        # 為什麼檢測 img_count 是因為寫法是圖片放在一般訊息以markdown url發送
        # 並沒有把圖片放在Embed的內容中，因此需要判斷圖片數量，因為不一定有圖片可以發送
        match = re.search(r'https://youtu\S*', twitter_entry)
        try:
            if int(img_count) > 0:
                if match:
                    # 這是一般訊息內容 + 匹配到 YT 網址
                    await channel.send(f'{twitter_all_img}  [ʏᴛ]({match.group(0)})')
                else:
                    # 這是一般訊息的內容 使用 channel.send 我放在 Embed 程式碼的上方讓照片先發送
                    await channel.send(twitter_all_img)
            elif match:
                # 如果 twitter_entry 有匹配到 youtube 網址就發送網址到訊息
                await channel.send(f'[ʏᴛ]({match.group(0)})')
        except AttributeError:
            logger.info("Twitter_dict.pkl 字典資訊處理成功，訊息準備發送前檢測到錯誤")
            logger.critical(
                "頻道ID不正確，無法發送Discord訊息"
            )
            logger.warning(
                "請確認class DCBot_Twitter(object): def channel_id 函式中的字典 channel ID 硬編碼值是否為正確 return資料型別是否是 int ?"
            )
            raise ("Discord 頻道ID不正確，終止🚫程式，請參考Log資訊獲得詳細錯誤訊息")

        # 這是Embed的內容，賦值給 dc_embed 方便判斷訊息是否發送，因為Embed一定有內容
        # 所以沒有像圖片一樣需要判斷式
        dc_embed = await channel.send(embed=embed, view=button_view)

        if dc_embed:
            logger.info(
                f'發送到 {ive_members} 頻道 / Twitter帳號: {twitter_id} / MD5: {MD5} ─ 🆗'
            )
            # 互斥鎖定，確保同時只會有一個執行緒在發送Discord訊息，避免同一條訊息被重複發送
            await cache_manager.dc_cache_async(MD5)
        else:
            logger.critical(
                f'發送到 {ive_members} 頻道 / Twitter帳號: {twitter_id} / MD5: {MD5}，⚠️ Discord 消息發送失敗'
            )

    @ client.event
    # Token順利登入後的主事件函式
    async def on_ready():
        # 給自己知道目前使用哪一個 Discord Token 來登入機器人的身份
        print(
            f"\033[90m{await get_formatted_current_time()}\033[0m",
            "\033[38;2;255;0;85m目前登入身份 --> \033[0m",
            f"\033[38;2;255;140;26m{client.user}\033[0m"
        )
        # 設定Discord 機器人狀態，詳細參考 https://discordpy.readthedocs.io/en/stable/api.html
        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="RESET ‐ IVE SWITCH"
            )
        )
        logger.info("Discord is ready!")
        # 第一次啟動會先跑一次主函式，之後就不會再跑了，除非重新啟動程式
        await send_embed()
        # 主檢測循環
        while True:
            # 主檢測循環，時間調整(秒為單位)
            await asyncio.sleep(13)
            await send_embed()

    @client.command()
    async def ping(ctx):
        await ctx.reply(f'Ping is **{round(client.latency * 1000)}** ms')

    # 定義Embed和訊息的主函式
    @client.event
    async def send_embed(twitter_dict=None):
        # 來自API_Twitter處理的字典資料，嘗試讀取本地 assets/Twitter_dict.pkl 字典

        twitter_dict = DCBot_Twitter.load_data_concurrently()

        if twitter_dict is None:
            logger.critical("嘗試檢查資料庫是否存在或已經損毀")
            raise ("PKL 資料庫遺失或資料不正確")

        # 迴圈讀取 twitter_dict value {MD5:values}
        for MD5, values in twitter_dict.items():
            # 訊息尚未被Discord發送成功前，字典 values 會有9個值
            if len(values) == 9 and values[8] is not None:
                # ☹︎ Value system_time 暫時沒想到用在哪裡，先當佔位變數 這是有序的 [List] 必須保持每個變數的位置和功能
                # 定義 9 個不同的函數解包字典 values 除了int(img_count)，其餘都是 string type
                twitter_author, twitter_link, twitter_entry, post_time, system_time, img_count, twitter_all_img, avatar_link, ive_members = values
                # 透過Slice string 網址得到 英文帳號名 和 作者原始 Twitter 主頁，再賦予給區域變數
                twitter_id = twitter_link[14:-27]
                author_link = twitter_link[:-27]
                # Embed上自訂的圖示，字典查詢使用
                minive_link = DCBot_Twitter.get_minive_link(ive_members)
                channel_id = DCBot_Twitter.channel_id(ive_members)

                # client.get_channel 是 Discord python 規定語法
                channel = client.get_channel(channel_id)

                # 創立一個Embed物件用來顯示推特訊息內容，物件賦予給 embed value
                embed = discord.Embed(
                    title='**' + twitter_author + '**',
                    url=author_link,
                    # Embed顏色設定，只能使用16進製的RGB值
                    color=0xbd9be0
                )

                embed.set_author(
                    name='ɴᴇᴡ ᴛᴡᴇᴇᴛ  ⎼  @' + twitter_id,
                    icon_url=minive_link,
                )

                no_img = False
                match twitter_all_img:
                    case None:
                        footer_icon = '📰　'
                        no_img = True
                    case _ if twitter_all_img[(len(twitter_all_img) - 4):-1] == 'mp4':
                        footer_icon = '🎬'
                    case _:
                        footer_icon = '🖼️'

                # 如果內文是轉推就提取轉推的帳號，並且刪除twitter_entry內的RT string
                if twitter_entry.startswith('RT'):
                    re_tweet = twitter_entry.strip().split('\n')[0]
                    twitter_entry = re.sub(
                        rf'{re_tweet}', ' \n',
                        twitter_entry)
                    # 重新slice給Discord當最終re_tweet value
                    re_tweet = f' ↪  {re_tweet[3:]}'
                else:
                    re_tweet = '  '

                # Embed 的主內容區，我填充了Twitter貼文內容
                embed.add_field(
                    name=re_tweet,
                    value=twitter_entry,
                    inline=False,
                )

                # Embed 的右上角小圖片區
                embed.set_thumbnail(url=avatar_link)

                # Embed 的右下角時間區，使用 datetime module 格式化時間
                # Embed 的時間要求要使用 datetime 物件傳遞值不能使用 string 會報錯
                embed.timestamp = datetime.strptime(
                    post_time, '%Y/%m/%d %H:%M:%S'
                )

                if no_img:
                    embed.set_footer(text=f'🅼🅸🆃  © 2024 𝐨𝐦𝐞𝐧𝐛𝐢𝐛𝐢    {footer_icon}',
                                     icon_url='https://i.meee.com.tw/caHwoj6.png')
                else:
                    # Embed 的頁尾區，顯示圖片數量，版權資訊
                    embed.set_footer(text=f'🅼🅸🆃  © 2024 𝐨𝐦𝐞𝐧𝐛𝐢𝐛𝐢    {footer_icon} ' + str(img_count),  # 注意只支持string格式，因此 img_count 要轉換為string
                                     # 這是Embed的頁尾小圖示，這邊使用 https://yesicon.app/skill-icons/twitter MIT © 圖庫的圖示
                                     # 圖床是臺灣 https://meee.com.tw/ ⓒ Meee 2023 版權所有
                                     icon_url='https://i.meee.com.tw/caHwoj6.png')

                # 創建一個按鈕此處是放在Embed的下方，按鈕設定為超連結按鈕
                # 連結指向原始貼文連結，詳細看 :133 class ButtonView
                button_view = ButtonView(url=twitter_link)

                # 異步傳遞 value 給 send_discord_message 函數
                # 這邊注意 img_count 要使用 int 型態傳遞，以利後續計算
                await send_discord_message(channel, ive_members, embed, button_view, twitter_id, twitter_all_img, MD5, img_count, twitter_entry)

    try:
        # 執行 Discord bot 程式
        client.run(DCBot_Twitter.load_DC_token())
    except ValueError as e:
        logger.error(e)
        raise ('請檢查 config 中 .env Discord_TOKEN 是否正確!')


if __name__ == '__main__':
    discord_twitter()
