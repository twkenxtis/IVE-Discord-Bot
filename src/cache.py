import json
import os
import pickle

from loguru import logger
# loguru is used under the MIT License
# Copyright (c) 2024 Delgan
# For more details, see the LICENSE file included with the distribution

def dc_cache(MD5):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_pkl = os.path.join(script_dir, '..', 'assets', 'Twitter_dict.pkl')
    file_path_json = os.path.join(script_dir, '..', 'assets', 'Twitter_dict.json')

    pkl_data = {}

    if os.path.exists(file_path_pkl):
        with open(file_path_pkl, 'rb') as pkl:
            pkl_data = pickle.load(pkl)

    if os.path.exists(file_path_json):
        with open(file_path_json, 'r') as j:
            json_dict = json.load(j)
    else:
        logger.error(f"Twitter_dict.pkl not found: {file_path_pkl} 或 Twitter_dict.json not found: {file_path_json}")

    value = 'SENDED'

    pkl_data[MD5] = list(pkl_data[MD5])

    pkl_data[MD5].append(value)
    json_dict[MD5].append(value)

    with open(file_path_pkl, 'wb') as pkl:
        pickle.dump(pkl_data, pkl)

    with open(file_path_json, 'w') as j:
        json.dump(json_dict, j, indent=4)
