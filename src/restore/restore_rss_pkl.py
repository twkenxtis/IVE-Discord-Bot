import json
import os
import pickle

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, '../../config/rss_list.json')
pickle_file_path = os.path.join(script_dir, "../../assets/rss_list.pkl")

# 讀取 JSON 檔案並將空的字符串替換為 None
with open(json_file_path, 'r') as j:
    loaded_json = json.load(j)
    processed_json = [item if item else None for item in loaded_json]

# 存入 pickle 檔案，只存入非 None 值
filtered_json_for_pickle = [
    item for item in processed_json if item is not None]

if filtered_json_for_pickle:
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(filtered_json_for_pickle, pickle_file)
