import json
import pickle
import os
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))
json_file = 'ive_hashtag.json'
backup_file = 'backup/backup.ive_hashtag.json'
if not os.path.isfile(json_file):
    shutil.copy2(backup_file, json_file)
    print('檢測到異常狀況，已還預設的json檔案')

with open(json_file, 'rb') as file:
    hashtag = json.load(file)

with open('../assets/ive_hashtag.pkl', 'wb') as file:
    pickle.dump(hashtag, file)

try:
    with open('../assets/ive_hashtag.pkl', 'rb') as file:
        loaded_data = pickle.load(file)
        print('檔案已經更新成功!')
except Exception as e:
    print('WARNING: Update Failed.')

print(loaded_data)
