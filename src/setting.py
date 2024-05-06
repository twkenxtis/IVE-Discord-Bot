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


def check_chrome_notify_log():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    setting_file = os.path.join('../config/setting.json')

    with open(str(setting_file), 'r') as json_file:
        setting_chrome_notify = json.load(json_file)

    chrome_notify = {
        'linux': setting_chrome_notify[1], 'win32': setting_chrome_notify[3]}

    platform = sys.platform
    if platform in chrome_notify:
        path = chrome_notify[platform]
        if os.path.exists(path):
            print('Successfully - Chrome notifications log file found.')
            print("\033[34mNotification of Continuous checking... \033[0m")
            logging.info(f"File found: {path}")
            return True, path
        else:
            (logging.error(f"File not found: {path}"))
            SystemExit(1)
    else:
        logging.warning("Unknown operating system")
        sys.stdout.flush()
        sys.exit(1)
