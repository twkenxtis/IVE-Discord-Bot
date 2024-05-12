import logging
import os

from src.API_notify import ChromeNotifyLogHandler
from src.custom_log import ColoredLogHandler
from src.setting import check_chrome_notify_log

# 設定基本的日誌設定

logging.basicConfig(
    level=logging.DEBUG, handlers=[ColoredLogHandler(fmt=logging.BASIC_FORMAT)]
)


class Setup:

    def __init__(self):
        current_dir = os.getcwd()
        self.history_path = os.path.join(current_dir, "assets", "notify_history.txt")
        self.check_setting_file()
        self.check_notify_history()
        self.set_path_and_double_check()
        self.sync_notify_000003_log()
        self.check_history_file_size()

    def check_setting_file(self):
        if check_chrome_notify_log() is None:
            raise SystemExit("ERROR: 設定檔路徑可能有錯誤，導致無法找到Chrome通知日誌")
        else:
            return list(check_chrome_notify_log())

    def check_notify_history(self):
        history_file = self.history_path

        if os.path.isfile(history_file):
            pass
        else:
            with open(self.history_path, "w", encoding="utf-8"):
                print("notify_history.txt 檔案建立成功！", self.history_path)
        return self.history_path

    def set_path_and_double_check(self):
        history_file = self.history_path
        return_path = self.check_setting_file()

        if return_path is not None:
            patch_000003_log = return_path[1]
        elif os.path.isfile(history_file):
            history_file = history_file
        else:
            self.check_notify_history()
        return patch_000003_log, history_file

    def sync_notify_000003_log(self):
        patch_000003_log, history_file = self.set_path_and_double_check()

        with open(patch_000003_log, "r", encoding="utf-8", errors="ignore") as bin_log:
            chrome_000003_log = bin_log.readlines()
        with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
            history_log = f.readlines()
        with open(history_file, "w", encoding="utf-8", errors="ignore") as f:
            history_log = f.writelines(chrome_000003_log)
        if self.check_history_file_size() is True:
            print("\033[96mChrome 通知日誌與本地通知歷史日誌檔案同步成功！\033[0m")

            # 初始化完成，開始監聽Chrome通知日誌
            ChromeNotifyLogHandler().main()
            pass

    def check_history_file_size(self, depth=0):
        path = self.history_path

        if depth >= 10:
            logging.error("檔案同步失敗，請重新運行程式!")
            return False
        try:
            file_size = os.path.getsize(path)

            if file_size > 1:
                return True
            else:
                parent_dir = os.path.dirname(path)
                return self.check_history_file_size(parent_dir, depth + 1)
        except FileNotFoundError:
            logging.error(f"找不到檔案 {path}")
            return False


if __name__ == "__main__":
    Setup()
