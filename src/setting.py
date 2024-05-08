import logging
import os
import sys
import json

from custom_log import ColoredLogHandler


logging.basicConfig(
    level=logging.INFO,
    handlers=[ColoredLogHandler(
        fmt=logging.BASIC_FORMAT, file_path='./logs\\log.txt', debug_file_path='./logs\\DEBUG_log.txt')],
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
setting_file = os.path.join('../config/setting.json')


def check_chrome_notify_log():

    global setting_file

    with open(str(setting_file), 'r') as json_file:
        setting_chrome_notify = json.load(json_file)

    chrome_notify = {
        'linux': setting_chrome_notify[1], 'win32': setting_chrome_notify[3]}

    platform = sys.platform
    if platform in chrome_notify:
        path = chrome_notify[platform]
        if os.path.exists(path):
            logging.info(f"File found: {path}")
            print(
                '\033[38;2;255;255;153mSuccessfully\033[m - \033[38;2;204;245;255mChrome notifications log file found!\033[m')
            print(
                '\033[38;2;153;235;255mNotification of Continuous checking...\033[m')
            return True, path
        else:
            (logging.error(f"File not found: {path}"))
            SystemExit(1)
    else:
        logging.warning("Unknown operating system")
        sys.stdout.flush()
        sys.exit(1)
