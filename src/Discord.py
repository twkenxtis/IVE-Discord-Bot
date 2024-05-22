# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import logging
import os
import pickle
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

from cache import cache_manager
from timezone import get_formatted_current_time

import discord
from discord.ext import commands
# from discord import Embed
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
            os.path.join(os.path.dirname(__file__), "..",
                         "assets", "Twitter_dict.pkl")
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
        # 使用ProcessPoolExecutor創建進程池進行並發執行
        with ProcessPoolExecutor() as executor:
            # 提交load_pickle_dict方法至進程池執行，並使用result()等待結果返回
            return executor.submit(DCBot_Twitter.load_pickle_dict).result()

    @staticmethod
    def load_DC_token():
        # 獲取當前腳本所在目錄
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 打開.env文件
        with open(os.path.join(script_dir, '..', 'config', '.env'), 'r') as env_file:
            # 逐行讀取文件
            for line in env_file:
                # 如果該行以'Discord_TOKEN'開頭
                if line.startswith('Discord_TOKEN'):
                    # 返回等號後的值，並去除空格
                    return line.split('=')[1].strip()

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
            "GROUPS": "https://i.imgur.com/WnkrrJS.png"
        }

        if minive_link.get(ive_name) is not None:
            return minive_link.get(ive_name)

        logger.error(
            "無法匹配到對應成員的Minive URL，請檢查PKL字典-> Value[8] 是否是正確的成員名稱或GROUPS")
        raise ValueError('Minive url match failed')

    @staticmethod
    @ lru_cache(maxsize=7)
    def channel_id(ive_name):
        channel_dict = {
            "GAEUL": "1242763427277963286",
            "fallingin__fall": "1242763427277963286",
            "YUJIN": "1242763450971586641",
            "_yujin_an": "1242763450971586641",
            "REI": "1242763473746661426",
            "reinyourheart": "1242763473746661426",
            "WONYOUNG": "1242763495339065407",
            "for_everyoung10": "1242763495339065407",
            "LIZ": "1242763521003884576",
            "liz.yeyo": "1242763521003884576",
            "LEESEO": "1242763542873247806",
            "eeseooes": "1242763542873247806",
            "GROUPS": "1242763566264614948"
        }
        return int(channel_dict.get(ive_name))


class ButtonView(discord.ui.View):
    def __init__(self, url: str, timeout: float | None = 60):
        # 初始化函數，設置超時時間
        super().__init__(timeout=timeout)

        # 創建一個連結按鈕
        url_button = discord.ui.Button(
            label="View on X",
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
intents = discord.Intents.default()
intents.message_content = True
# 前綴設定
client = commands.Bot(command_prefix='!!', intents=intents)


def discord_twitter():

    async def send_discord_message(channel, ive_members, embed, button_view,
                                   twitter_id, twitter_all_img, MD5, img_count,
                                   ):
        if img_count > 0:
            await channel.send(twitter_all_img)
            # await channel.send("**開發者模式**")

        dc_embed = await channel.send(embed=embed, view=button_view)
        if dc_embed:
            cache_manager.dc_cache(MD5)
            logger.info(
                f'發送到 {ive_members} 頻道 / Twitter帳號: {twitter_id} / MD5: {MD5} ─ OK'
            )
        else:
            logger.critical(f'Twitter帳號: {twitter_id}，Discord 消息發送失敗')

    @ client.event
    async def on_ready():
        # 給自己知道目前使用的Discord Token登入機器人的身份
        print(
            f"\033[90m{await get_formatted_current_time()}\033[0m",
            "\033[38;2;255;0;85m目前登入身份 --> \033[0m",
            f"\033[38;2;255;140;26m{client.user}\033[0m"
        )
        # Discord 機器人狀態
        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="Accendio"
            )
        )
        await send_embed()

    @client.command()
    async def ping(ctx):
        await ctx.reply(f'Ping is **{round(client.latency * 1000)}** ms')

    @client.event
    async def send_embed():
        try:
            twitter_dict = DCBot_Twitter.load_data_concurrently()
        except FileNotFoundError as e:
            logger.error(e)
        except ValueError as e:
            logger.error(e)

        for MD5, values in twitter_dict.items():
            if len(values) == 9:
                twitter_author, twitter_link, twitter_entry, post_time, system_time, img_count, twitter_all_img, avatar_link, ive_members = values

                twitter_id = twitter_link[20:-27]
                author_link = twitter_link[:-27]
                minive_link = DCBot_Twitter.get_minive_link(ive_members)
                channel_id = DCBot_Twitter.channel_id(ive_members)

                channel = client.get_channel(channel_id)

                embed = discord.Embed(
                    title='**' + twitter_author + '**',
                    url=author_link,
                    color=0xed68a6
                )

                embed.set_author(
                    name='ɴᴇᴡ ᴛᴡᴇᴇᴛ  ⎼  @' + twitter_id,
                    icon_url=minive_link,
                )

                embed.add_field(
                    name='　',
                    value=twitter_entry,
                    inline=False,
                )

                embed.set_thumbnail(url=avatar_link)

                embed.timestamp = datetime.strptime(
                    post_time, '%Y/%m/%d %H:%M:%S'
                )

                embed.set_footer(text='🅼🅸🆃 © 2024 ᴏᴍᴇɴʙɪʙɪ    🖼️ ' + str(img_count),
                                 icon_url='https://i.meee.com.tw/caHwoj6.png')

                button_view = ButtonView(url=twitter_link)

                await send_discord_message(channel, ive_members, embed, button_view, twitter_id, twitter_all_img, MD5, int(img_count))
            else:
                logger.info(f"此訊息: {MD5} 已經發送過不再次發送")

    try:
        client.run(DCBot_Twitter.load_DC_token())
    except ValueError as e:
        logger.error(e)


if __name__ == '__main__':
    discord_twitter()
