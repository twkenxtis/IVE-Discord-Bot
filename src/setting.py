import json
import logging
import os
import sys


logging.basicConfig(
    level=logging.INFO,
)


def check_chrome_notify_log():

    current_dir = os.getcwd()
    setting_file = os.path.join(current_dir, '../config', 'setting.json')
    

    with open(str(setting_file), 'r') as json_file:
        setting_chrome_notify = json.load(json_file)

    chrome_notify = {
        'linux': setting_chrome_notify[1], 'win32': setting_chrome_notify[3]}

    platform = sys.platform
    if platform in chrome_notify:
        path = chrome_notify[platform]
        if os.path.exists(path):
            return True, path
        else:
            (logging.error(f"File not found: {path}"))
            print("\033[38;2;255;255;153mPlease check the path of 'Chrome notifications log file' in /config/setting.json. \033[0m")
            SystemExit(1)
    else:
        logging.warning("Unknown operating system")
        sys.stdout.flush()
        sys.exit(1)
