# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
import asyncio
import importlib.metadata
import json
import logging
import os
import pickle
import random
import sys
import time
from datetime import datetime, timedelta
from typing import Generator, List, Tuple, Optional

from src.API_Twitter import start_API_Twitter

from loguru import logger
# loguru is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution
import packaging.specifiers
# packaging is under the Apache License 2.0
# Copyright (c) 2004 sbidoul
# For more details, see the LICENSE file included with the distribution
import toml
# toml is used under the MIT License
# Copyright 2013-2019 William Pearson, 2015-2016 Julien Enselme, 2016 Google Inc., 2017 Samuel Vasko,
# Copyright 2017 Nate Prewitt, 2017 Jack Evans 2019 Filippo Broggini
# For more details, see the LICENSE file included with the distribution


class Try_file:

    def __init__(self):
        self.try_assets()
        self.check_dependencies()
        RSS_List_Pop_up().run()

    def try_assets(self):
        PKL_PATH = os.path.join(os.path.dirname(__file__),
                                "assets", "Twitter_dict.pkl")
        JSON_PATH = os.path.join(os.path.dirname(__file__),
                                 "assets", "Twitter_dict.json")
        LOGS_DIR = os.path.join(os.path.dirname(__file__),
                                "assets", "logs")
        if not os.path.exists(PKL_PATH):
            with open(PKL_PATH, "wb") as f:
                logger.info(f"{PKL_PATH} 不存在，已初始化空字典建立")
                pickle.dump({}, f)
            with open(JSON_PATH, "w") as f:
                logger.info(f"{JSON_PATH} 不存在，已初始化空字典建立")
                json.dump({}, f)
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
            logger.info(f"日誌檔案夾 {LOGS_DIR} 不存在，已建立")

        try:
            with open(JSON_PATH, "r") as j:
                json.load(j)
        except json.decoder.JSONDecodeError:
            with open(JSON_PATH, "w") as j:
                json.dump({}, j)

    def check_dependencies(self):
        os.chdir(os.path.dirname(__file__))
        with open("dependencies.toml", "r") as f:
            dependencies_toml = toml.load(f)

        dependencies = dependencies_toml.get("dependencies", {})

        for package, version_constraint in dependencies.items():
            try:
                version = importlib.metadata.version(package)
                if version_constraint:
                    specifier = packaging.specifiers.SpecifierSet(
                        str(version_constraint))
                    if not packaging.version.parse(version) in specifier:
                        logging.error(
                            f"{package} version {version} does not meet the requirement {version_constraint}")
                        raise RuntimeError(
                            f"{package} version {version} does not meet the requirement {version_constraint}")
            except importlib.metadata.PackageNotFoundError:
                logging.error(f"{package} is not installed")
                raise RuntimeError(f"{package} is not installed")


class RSS_List_Pop_up:

    def __init__(self):
        rss_list_json_path = os.path.join(os.path.dirname(__file__),
                                          "config", "rss_list.json")
        self.rss_list_json_path = rss_list_json_path
        pass

    def load_RSSHUB_url(self) -> str:
        # 獲取當前腳本所在目錄
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 打開.env文件
        try:
            with open(os.path.join(script_dir, 'config', '.env'), 'r') as env_file:
                # 逐行讀取文件
                for line in env_file:
                    # 如果該行以'RSS_HUB_URL'開頭
                    if line.startswith('RSS_HUB_URL'):
                        # 返回等號後的值，並去除空格
                        return line.split('=')[1].strip()

                logger.critical("無法於環境變數文件找到 RSS_HUB_URL 值")
                raise ValueError("請確認.env文件是否包含 RSS_HUB_URL 欄位")
        except FileNotFoundError:
            logger.error("找不到.env文件，請重新建立環境變數檔案")
            raise FileNotFoundError("找不到.env文件，請重新建立環境變數檔案")

    def popup_list(self, input_list: List[str]) -> Generator[str, None, None]:
        random.shuffle(input_list)  # 直接打亂列表順序
        while input_list:
            yield input_list.pop(0)  # 彈出元素

    def special_function(self, rss_list: List[str]) -> None:
        # 這是特定時間觸發的功能
        logger.info("開始執行主程式")

        rsshub_url = self.load_RSSHUB_url()

        # 逐步列印列表的值
        for url in self.popup_list(rss_list):

            # 組合 rsshub 請求網址
            url = f"{rsshub_url}twitter/media/{url}"

            asyncio.run(start_API_Twitter(url).get_response())
            # 決定下次迭代間的等待時間
            wait_time = random.randint(19, 97)
            sys.stdout.write("\r")  # 返回行首，用於在同一行更新文本
            print(f"\x1B[38;2;255;77;166m下次請求將在\033[0m"
                  f"\033[38;2;230;230;0m {wait_time} \033[0m"
                  "\x1B[38;2;255;77;166m秒後...\033[0m")
            time.sleep(wait_time)
            if len(rss_list) == 0:  # 如果 rss_list 為空，則跳出外層循環
                break

    def check_time_trigger(self, trigger_times: List[Tuple[int, int]]) -> bool:
        """
        檢查當前時間是否與任何一個觸發時間相符。

        參數:
        trigger_times (list): 包含多個時間元組的列表，每個元組包含小時和分鐘。

        返回值:
        bool: 如果當前時間與任何一個觸發時間相符，返回 True，否則返回 False。
        """
        now = datetime.now().time()  # 獲取當前時間的時、分、秒部分
        # 遍歷所有觸發時間
        for start_time in trigger_times:
            # 比較當前時間的時、分是否與觸發時間相符
            if now.hour == start_time[0] and now.minute == start_time[1]:
                return True  # 如果相符，返回 True
        return False  # 如果沒有相符的觸發時間，返回 False

    def get_next_trigger_time(self, trigger_times: List[Tuple[int, int]]) -> Optional[datetime]:
        """
        獲取下一個觸發時間。

        參數:
        trigger_times (list): 包含多個時間元組的列表，每個元組包含小時和分鐘。

        返回值:
        datetime 或 None: 如果有下一個觸發時間，返回該時間的 datetime 對象，否則返回 None。
        """
        now = datetime.now()  # 獲取當前時間的完整 datetime 對象
        today_trigger_times = [
            # 將今天的日期與午夜時間結合，作為基準時間
            datetime.combine(now.date(), datetime.min.time())
            # 添加每個觸發時間的時、分部分，得到今天的觸發時間
            + timedelta(hours=t[0], minutes=t[1])
            for t in trigger_times
        ]
        # 過濾出今天剩餘的觸發時間（即未來時間）
        future_times = [t for t in today_trigger_times if t > now]
        # 如果有未來的觸發時間，返回最早的一個
        if future_times:
            return min(future_times)
        # 如果今天沒有剩餘的觸發時間，返回明天的第一個觸發時間
        if trigger_times:
            return datetime.combine(
                now.date() + timedelta(days=1), datetime.min.time()
            ) + timedelta(hours=trigger_times[0][0], minutes=trigger_times[0][1])
        return None  # 如果沒有觸發時間，返回 None

    def clear_terminal(self) -> None:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def run(self) -> None:
        try:
            # 讀取並初始化列表
            with open(self.rss_list_json_path, "r") as j:
                rss_list = json.load(j)
        except FileNotFoundError:
            logger.critical("找不到 RSS 列表文件，請確認 config/rss_list.json 是否存在!")
            raise (
                f"File path: {self.rss_list_json_path} rss_list.json File not found"
            )

        # 定義多個觸發時間（24小時製）
        trigger_times = [
            (9, 0), (12, 0), (16, 0), (20, 0), (24, 00), (6, 0)
        ]
        try:
            while True:
                now = datetime.now()
                if self.check_time_trigger(trigger_times):
                    self.special_function(rss_list)  # 觸發特定功能
                    rss_list = json.load(open(
                        self.rss_list_json_path,
                        "r")
                    )  # 重新初始化 rss_list
                    continue
                next_trigger_time = self.get_next_trigger_time(trigger_times)

                self.clear_terminal()  # 清除畫面

                if next_trigger_time:
                    time_until_next_trigger = (
                        next_trigger_time - now
                    ).total_seconds()

                    print(
                        f"\033[96m24HR \033[0m\033[95;1m下次請求將在\033[0m",
                        # 格式化下一個觸發時間點。
                        f"\033[93;1m{next_trigger_time.strftime('%H:%M:%S')}\033[0m",
                        "\033[95;1m開始循環請求函式\033[0m",
                    )
                    # 倒數計時列印
                    for remaining in range(int(time_until_next_trigger), 0, -1):
                        hours, rem = divmod(remaining, 3600)
                        minutes, seconds = divmod(rem, 60)
                        time_format = f"{hours:02}:{minutes:02}:{seconds:02}"
                        sys.stdout.write("\r")
                        sys.stdout.write(f"\x1B[38;2;255;77;166m🔄 倒數計時中...\033[0m"
                                         f"\033[93;1m  {time_format} \033[0m"
                                         "\x1B[38;2;255;77;166m後開始發送循環請求\033[0m")
                        sys.stdout.flush()
                        time.sleep(1)
        except FileNotFoundError:
            logger.critical("找不到 RSS 列表文件，請確認 config/rss_list.json 是否存在!")
            raise (
                f"File path: {self.rss_list_json_path} rss_list.json File not found"
            )
        except KeyboardInterrupt:
            sys.stdout.write("\r")
            logger.info("手動取消程式執行")
            pass


if __name__ == '__main__':
    Try_file()
