# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import logging
import os
import pickle
from datetime import datetime
from functools import lru_cache

from aiocache import cached, Cache
# aiocache - BSD 3-Clause License
# Copyright (c) 2016, Manuel Miranda de Cid
# For more details, see the LICENSE file included with the distribution
import discord
from discord.ext import commands
from discord import Embed
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
    def load_DC_token():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, '..', 'config', '.env'), 'r') as env_file:
            for line in env_file:
                if line.startswith('Discord_TOKEN'):
                    return line.split('=')[1].strip()
    
    @staticmethod
    @ lru_cache(maxsize=None)
    def load_pickle_dict() -> str:
        pkl_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..",
                         "assets", "Twitter_dict.pkl")
        )
        if not os.path.isfile(pkl_file):
            logger.error(f"pkl_file: {pkl_file} 文件不存在")
            raise FileNotFoundError(f"pkl_file: {pkl_file} 文件不存在，請確認路徑是否正確")

        with open(pkl_file, "rb") as pkl:
            pkl_data = pickle.loads(pkl.read(), fix_imports=True)
            return pkl_data
   
    @ lru_cache(maxsize=12)
    def get_minive_link(ive_name: str) -> str:
        minive_link = {
            "GAEUL": "https://i.imgur.com/H8dA0kV.png",
            "fallingin__fall": "https://i.imgur.com/H8dA0kV.png",
            "YUJIN": "https://i.imgur.com/jgYovTl.png",
            "_yujin_an": "https://i.imgur.com/jgYovTl.png",
            "REI": "https://i.imgur.com/K73vFNP.png",
            "reinyourheart": "https://i.imgur.com/K73vFNP.png",
            "WONYOUNG": "https://i.imgur.com/pe2k3p7.png",
            "for_everyoung10": "https://i.imgur.com/pe2k3p7.png",
            "LIZ": "https://i.imgur.com/Au63MYD.png",
            "liz.yeyo": "https://i.imgur.com/Au63MYD.png",
            "LEESEO": "https://i.imgur.com/yBF6lpY.png",
            "eeseooes": "https://i.imgur.com/yBF6lpY.png",
            "GROUPS": "https://i.imgur.com/GcBL6V9.png"
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
        return int(channel_dict.get(ive_name))

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

# Discord bot 全局設定
intents = discord.Intents.default()
intents.message_content = True
# 前綴設定為None，不使用預設的 !
client = commands.Bot(command_prefix=None, intents=intents)

def discord_twitter():

    async def send_discord_message(channel, ive_members, embed, button_view, twitter_id, twitter_all_img, MD5):
        dc_message = await channel.send(twitter_all_img)
        #dc_message = await channel.send("**開發者模式**")
        dc_embed = await channel.send(embed=embed, view=button_view)
        if dc_message and dc_embed:
            logger.info(
                    f'發送到 {ive_members} 頻道 / Twitter帳號: {twitter_id} / MD5: {MD5} ─ OK'
                    )
        else:
            logger.critical(f'Twitter帳號: {twitter_id}，Discord 消息發送失敗')


    @ client.event
    async def on_ready():
        # 給自己知道登入身分
        print(f"目前登入身份 --> {client.user}")
        # Discord 機器人狀態
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Accendio"))
        await send_embed()

    @ client.event
    async def send_embed():
        
        try:
            twitter_dict = DCBot_Twitter.load_pickle_dict()
        except FileNotFoundError as e:
            logger.error(e)
    
        dict_key = []
        for key in twitter_dict.keys():
            dict_key.append(key)
        
        value = []
        for key in twitter_dict.keys():
            for _ in twitter_dict.get(key):
                value.append(twitter_dict.get(key))
                break
            
        list_n = 0
        list_max = len(dict_key) - 1
        while list_n <= list_max:
            # 注意這裡要確保 list_n 不超出 value 列表的範圍
            if list_n < len(value):
                MD5 = dict_key[list_n]
                twitter_author = value[list_n][0] # 貼文作者
                twitter_link = value[list_n][1] # 貼文網址
                twitter_id = value[list_n][1][20:-27] # 貼文網址Slice得到tweet英文作者ID
                author_link = value[list_n][1][:-27] # 貼文網址Slice得到tweet英文作者ID
                twitter_entry = value[list_n][2] # Twitter 貼文內容
                post_time = value[list_n][3] # 2024/04/29 20:45:59 (貼文發布時間)
                img_count = str(value[list_n][5]) # int 照片數量
                twitter_all_img = value[list_n][6] # 所有貼文照片網址
                author_avatar = value[list_n][7]  # 貼文作者的頭像網址
                ive_members = value[list_n][8] # ive 成員名稱或GROUPS
                minive_link = DCBot_Twitter.get_minive_link(value[list_n][8])
                channel_id = DCBot_Twitter.channel_id(value[list_n][8])
                
                channel = client.get_channel(channel_id)
                
                embed = discord.Embed(
                    title= '**'+ twitter_author + '**',
                    url=author_link, color=0xed68a6)
                
                embed.set_author(
                    name='New tweet ─  @' + twitter_id,
                    icon_url=minive_link,
                )
                
                embed.add_field(
                    name='　',
                    value=twitter_entry,
                    inline=False,
                )
                
                embed.set_thumbnail(url=author_avatar)
                
                embed.timestamp = datetime.strptime(
                    post_time, '%Y/%m/%d %H:%M:%S')
                
                embed.set_footer(text='🅼🅸🆃 © 2024 ᴏᴍᴇɴʙɪʙɪ    🖼️ ' + img_count,
                                    icon_url='https://i.meee.com.tw/caHwoj6.png')
                
                button_view = ButtonView(url=twitter_link)
            
            else:
                logger.error(f"Index {list_n} is out of range in 'value' list.")
            # 確認完畢，List + 1 進入下一個迴圈直到字典遍歷完成
            list_n += 1

            await send_discord_message(channel, ive_members, embed, button_view, twitter_id, twitter_all_img, MD5)

    try:
        client.run(DCBot_Twitter.load_DC_token())
    except ValueError as e:
        logger.error(e)


if __name__ == "__main__":
    discord_twitter()
