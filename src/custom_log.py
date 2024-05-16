import asyncio
import logging


# 定義一個自定義的日誌處理器，繼承自 logging.StreamHandler
class ColoredLogHandler(logging.StreamHandler):
    def __init__(self, fmt=None, file_path=None, debug_file_path=None):
        super().__init__()
        self._fmt = fmt or logging.BASIC_FORMAT

        if file_path:
            self.file_path = file_path
            self.file_handler = logging.FileHandler(file_path)
            self.file_handler.setLevel(logging.WARNING)
            self.file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            self.file_handler.setFormatter(self.file_formatter)

        if debug_file_path:
            self.debug_file_path = debug_file_path
            self.debug_file_handler = logging.FileHandler(debug_file_path)
            self.debug_file_handler.setLevel(logging.DEBUG)
            self.debug_file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            self.debug_file_handler.setFormatter(self.debug_file_formatter)

    async def async_emit(self, record):
        await asyncio.to_thread(self.emit, record)

    def emit(self, record):
        super().emit(record)

        if hasattr(self, "file_handler") and record.levelno >= logging.WARNING:
            asyncio.create_task(self.async_emit(record))

        if hasattr(self, "debug_file_handler") and record.levelno == logging.DEBUG:
            asyncio.create_task(self.async_emit(record))


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
