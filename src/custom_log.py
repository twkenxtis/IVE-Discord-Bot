import logging


# 定義一個自定義的日誌處理器，繼承自 logging.StreamHandler
class ColoredLogHandler(logging.StreamHandler):
    def __init__(self, fmt=None, file_path=None, debug_file_path=None):

        # 呼叫父類別的建構函數
        super().__init__()

        # 定義不同等級的顏色映射
        self.color_mapping = {
            logging.DEBUG: "\033[92m",  # 淺綠色
            logging.INFO: "\033[96m",  # 青色
            logging.WARNING: "\033[38;5;214m",  # 金黃色
            logging.ERROR: "\x1b[31m",  # 深紅色
            logging.CRITICAL: "\033[91m",  # 深紫紅色
        }
        self.reset_color = "\033[0m"  # 重置顏色
        self._fmt = fmt or logging.BASIC_FORMAT

        # 如果指定了文件路徑，則創建一個文件處理器
        if file_path:
            self.file_handler = logging.FileHandler(file_path)
            self.file_handler.setLevel(logging.WARNING)
            self.file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            self.file_handler.setFormatter(self.file_formatter)

        # 如果指定了 debug 文件路徑，則創建一個 debug 文件處理器
        if debug_file_path:
            self.debug_file_handler = logging.FileHandler(debug_file_path)
            self.debug_file_handler.setLevel(logging.DEBUG)
            self.debug_file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
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
        if hasattr(self, "file_handler") and record.levelno >= logging.WARNING:
            self.file_handler.emit(record)

        # 如果有 debug 文件處理器，則將日誌訊息寫入到 debug 文件
        if hasattr(self, "debug_file_handler") and record.levelno == logging.DEBUG:
            self.debug_file_handler.emit(record)


if __name__ == "__main__":

    # 設定基本的日誌設定
    logging.basicConfig(
        level=logging.INFO, handlers=[
            ColoredLogHandler(fmt=logging.BASIC_FORMAT)]
    )

    # 取得日誌物件
    logging.getLogger().info("INFO MESSAGE")
    logging.getLogger().debug("DEBUG MESSAGE")
    logging.getLogger().warning("WARNING MESSAGE")
    logging.getLogger().error("ERROR MESSAGE")
    logging.getLogger().critical("CRITICAL MESSAGE")
