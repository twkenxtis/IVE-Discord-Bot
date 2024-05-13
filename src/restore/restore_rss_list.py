import os
import pickle
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, '../../config/rss_list.json')

default_json_file = [
    "fallingin__fall",
    "_yujin_an",
    "reinyourheart",
    "for_everyoung10",
    "liz.yeyo",
    "eeseooes",
    "ROSE_AYJ0901",
    "DearKitty_liz",
    "LOME924",
    "Flippedberry",
    "qcpk0203",
    "roysix_",
    "901Percent_",
    "double_x21",
    "Daisy_Lnn",
    "yaoyaohu070221",
    "DIVE_LIZ_1101",
    "Pichoni20040203",
    "DearHerbst924",
    "lycheee_lii",
    "silky_ls",
    "Scent_dolls",
    "Lizz_among",
    "DIVE_LIZ_1101",
    "ive_Liz_mom",
    "kaokao_honey",
    "EV_ICeleb",
    "nyoungighting",
    "831young_hee626",
    "Broivn_0831",
    "10_vickycat",
    "pompompurin924",
    "saladwanA",
    "imhyeon29764440",
    "Lizz_1121",
    "lux_0203",
    "Reively0203",
    "libeudesu",
    "sunflower203_",
    "B1ABEC_REI",
    "MottoRei0203",
    "rei_yalltake",
    "kirei__rei",
    "miaodakasi77125",
    "yaoyaohu070221",
    "eeseooes_leeseo",
    "Listen_0221",
    "Richu_Pyonpyon",
    "CherrBunny_0831",
    "OneYoung_10",
    "122Euphoria",
    "zhiwuzhiying",
    "Autumn924_",
    "my_angels____",
    "SUNSET4H",
    "rkpn15e",
    "Daisy_Lnn",
    "WYJUICE0831",
    "wywjsy1",
    "901Percent_",
    "kirei_rei",
    "cotton__rei",
    "Meory1121",
    "GoldenAgeYJ",
    "andingding901",
    "JjangGU_030901",
    "asa80132",
    "Katalina_924",
    "zaijienantao924",
    "B924gold",
    "Snooze_0831",
    "LOTSO_NOTSO",
    "snow_ayjjwy",
    "PinkPeach_rei",
    "Eudemonic_kr",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    ""
]


# 寫入原始 JSON 檔案
with open(json_file_path, 'w') as j:
    json.dump(default_json_file, j, indent=4)

# 讀取 JSON 檔案並將空的字符串替換為 None
with open(json_file_path, 'r') as j:
    loaded_json = json.load(j)
    processed_json = [item if item else None for item in loaded_json]

# 存入 pickle 檔案，只存入非 None 值
filtered_json_for_pickle = [
    item for item in processed_json if item is not None]

if filtered_json_for_pickle:
    pickle_file_path = os.path.join(
        script_dir, "../../assets/rss_list.pkl")
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(filtered_json_for_pickle, pickle_file)
