import logging
import json
import os
import pickle
import subprocess
import time

class ColoredLogHandler(logging.StreamHandler):
    def __init__(self, fmt=None):
        super().__init__()
        # 定義不同等級的顏色映射
        self.color_mapping = {
            logging.DEBUG:'\033[92m',           # 浅绿色
            logging.INFO:'\033[96m',            # 青色
            logging.WARNING:'\033[38;5;214m',   # 金黃色
            logging.ERROR:'\x1b[31m',           # 深红色
            logging.CRITICAL:  '\033[91m',      # 深紫红色
        }
        self.reset_color = '\033[0m'  # 重置颜色
        self._fmt = fmt or logging.BASIC_FORMAT

    def format(self, record):
        # 取得日誌訊息的顏色格式
        color_format = f"{self.color_mapping.get(record.levelno, '')}{self._fmt}{self.reset_color}"
        formatter = logging.Formatter(color_format)
        return formatter.format(record)


class Twitter_account_list:

    logging.basicConfig(level=logging.INFO,handlers=[ColoredLogHandler()])

    def __init__(self):
        self.pickle_file_path = ['']
        script_dir, json_file_path, savebin_file_path, pickle_file_path = self.check_rss_list_json_file()
        self.check_rss_list_status(script_dir, json_file_path,
                                   savebin_file_path, pickle_file_path)

    def check_rss_list_json_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        RESTORE_LIST_path = os.path.join("..//restore//restore_rss_list.py")
        RESTORE_PKL_path = os.path.join("..//restore//restore_rss_pkl.py")
        json_file_path = os.path.join(script_dir, "../../config/rss_list.json")
        savebin_file_path = os.path.join(script_dir, "../../assets/temp/json_file_size.bin")
        pickle_file_path = os.path.join(script_dir, "../../assets/rss_list.pkl")
        error_printer_path = json_file_path[-21:]

        # 檢查是否存在 rss_list.json 文件
        if os.path.isfile(json_file_path) is False:
            logging.warning(
            " 檢測到異常，已初始化 /config/rss_list.json "
            f"請重新於{error_printer_path} 重新設定JSON檔案!"
            )
            subprocess.run(['python', RESTORE_LIST_path])
        # 檢查是否存在 rss_list.pkl 文件
        elif os.path.isfile(pickle_file_path) is False:
            logging.warning(
            " 檢測到異常，已初始化 /config/rss_list.json "
            f"請重新於{error_printer_path} 重新設定JSON檔案!"
            )
            subprocess.run(['python', RESTORE_LIST_path])
            subprocess.run(['python', RESTORE_PKL_path])
            time.sleep(1)
        else:
            # 預留空白區域
            pass

        return script_dir, json_file_path, savebin_file_path, pickle_file_path

    def binary_search(self, low, high, value):
        if low <= high:
            mid = (low + high) // 2
            guess = self.pickle_file_path[mid]

            if guess == value:
                if guess == '':
                    return False, 'Not found'
                else:
                    return True, guess
            elif guess < value:
                return self.binary_search(mid + 1, high, value)
            else:
                return self.binary_search(low, mid - 1, value)
        else:
            return False, 'Not found'

    def search(self, value):
        return self.binary_search(0, len(self.pickle_file_path) - 1, value)

    def check_rss_list_status(self, script_dir, json_file_path, savebin_file_path, pickle_file_path):
        with open(str(json_file_path), 'r') as j:
            json_data = json.load(j)
            # 將 json_data 中的空值 (None) 替換為 None，以便後續處理
            processed_json = [i if i else None for i in json_data]

        # 讀取 JSON 檔案的大小，並將其存儲在 current_file_size 變數中
        current_file_size = os.path.getsize(json_file_path)
        # 讀取二進製檔案 savebin_file_path 的內容，並將其轉換為整數 previous_file_size
        with open(savebin_file_path, "rb") as f:
            previous_file_size = int.from_bytes(f.read(), "big")
        # 將 current_file_size 轉換為二進製數據，並寫入到 savebin_file_path 檔案中
        with open(savebin_file_path, "wb") as f:
            f.write(current_file_size.to_bytes(4, "big"))

        # 檢測 rss_list.json 檔案大小是否有變化
        file_size_changed = current_file_size != previous_file_size
        if file_size_changed:
            print(
                f"\033[38;2;255;26;175mJSON file size changed:\033[0m \033[38;2;128;255;255m{file_size_changed}\033[0m")
            # 存入 pickle 檔案，只存入非 None 值
            filtered_json_for_pickle = [
                item for item in processed_json if item is not None]
            if filtered_json_for_pickle:
                # 更新 JSON 資料轉換為 pickle 格式
                with open(pickle_file_path, 'wb') as pickle_file:
                    pickle.dump(filtered_json_for_pickle, pickle_file)
                    logging.info(
                        "rss_list.json transformed to rss_list.pkl successfully!")
                    self.pickle_file_path = pickle_file_path

        # main code for binary search data
        path_to_pk1 = os.path.join(script_dir, '../../assets/rss_list.pkl')
        with open(path_to_pk1, 'rb') as _pickle:
            self.pickle_file_path = pickle.load(_pickle)
            self.pickle_file_path = sorted(self.pickle_file_path)


# Development
if __name__ == "__main__":
    # TODO: 空值的話要None防止錯誤 還有資料型別只能是str，硬編碼在binary_search
    value_to_search = ''
    result = Twitter_account_list().search(value_to_search)
    print(type(result[0]))
    print(type(result[1]))
    print(result)
    print((result[0]))
    print((result[1]))
