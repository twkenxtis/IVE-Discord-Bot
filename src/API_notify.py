import logging
import os
import time

from custom_log import ColoredLogHandler
from setting import check_chrome_notify_log


logging.basicConfig(
    level=logging.INFO,
    handlers=[ColoredLogHandler(
        fmt=logging.BASIC_FORMAT, file_path='./logs\\log.txt', debug_file_path='./logs\\DEBUG_log.txt')],
)


# 相對路徑讀出 notify_history.txt 檔案路徑
project_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
history_path = os.path.join(project_dir, 'assets', 'notify_history.txt')

# 獲取 history.txt 檔案路徑


def read_notify_history_file():
    # 如果 history.txt 不存在，則建立新檔案
    if not os.path.exists(history_path):
        with open(history_path, "w", encoding="utf-8"):
            logging.warning("檢測到 notify_history.txt 不存在已建立新檔案！")
    return history_path


# 從 setting 物件開啟程式入口，得到 True 和 000003.log 路徑
try:
    boolean, patch_000003_log = check_chrome_notify_log()
    chrome_003_log = patch_000003_log
    # notify_history.txt
    history_file = read_notify_history_file()
except TypeError as e:
    SystemExit(e)


def check_file_changes(chrome_003_log):
    file_size = os.path.getsize(chrome_003_log)
    while True:
        # 檢查檔案大小是否有變化
        current_size = os.path.getsize(chrome_003_log)
        if current_size != file_size:
            file_size = current_size
            return True
        time.sleep(1)  # Default 1


def get_new_data(chrome_003_log, history_file):
    # 使用 with 語句開啟兩個文件，chrome_003_log 和 history_file
    # old 和 temp 是這兩個文件的別名 分別對應 000003.log 和 notify_history.txt
    with open(chrome_003_log, "r", encoding="utf-8", errors="ignore") as old, open(history_file, "r", encoding="utf-8", errors="ignore") as temp:
        # 讀取 old 文件的所有行，並將其存儲在 old_data 變數中
        old_data = old.readlines()
        # 讀取 temp 文件的所有行，並將其存儲在 temp_data 變數中
        temp_data = temp.readlines()
        # 錯誤檢測，如果 history.txt 異常，則建立新檔案，並強制寫入一次更新檔案
        # TODO: 這裡應該要加上更多的錯誤檢測 000003.log 異常目前無法處理只有實現一邊history.txt的檢測
        for _ in range(1):
            if len(old_data) < len(temp_data):
                with open(history_path, "w", encoding="utf-8"):
                    logging.warning("檢測到文件異常，已經重新同步 notify_history.txt")
                    logging.warning("路徑：", history_path)
                    with open(history_file, "w", encoding="utf-8", errors="ignore") as temp:
                        temp.writelines(old_data)
        # 檢查是否有新資料寫入 000003.log
        if len(old_data) > len(temp_data):
            new_data = old_data[len(temp_data):]  # 取得新資料
            # 如果000003.log有新資料，將更新資料寫入 history.txt
            with open(history_file, "a", encoding="utf-8", errors="ignore") as temp:
                temp.writelines(new_data)
            return (new_data)
        else:
            # 如果old_data的長度不大於temp_data的長度，返回None
            return None


def main():
    try:
        while True:
            if check_file_changes(chrome_003_log):
                _new_data = get_new_data(chrome_003_log, history_file)
                if _new_data is not None:
                    format_end_data = "".join(_new_data[1:])
                    print(str(format_end_data))
            # set timeout to checking new data coming from 000003.log
            time.sleep(0.5)
    except NameError:
        SystemExit(1)


if __name__ == "__main__":
    main()
