# IVE-Discord-Bot is used under the MIT License
# Copyright (c) 2024 twkenxtis (ytiq8nxnm@mozmail.com)
# For more details, see the LICENSE file included with the distribution
from functools import lru_cache

tag_dict = {
    "#가을": ["GAEUL"],
    "#gaeul": ["GAEUL"],
    "#Gaeul": ["GAEUL"],
    "#GAEUL": ["GAEUL"],
    "#ガウル": ["GAEUL"],
    "#김가을": ["GAEUL"],
    "#ANYUJIN": ["YUJIN"],
    "#YUJIN": ["YUJIN"],
    "#안유진": ["YUJIN"],
    "#유진": ["YUJIN"],
    "#REI": ["REI"],
    "#rei": ["REI"],
    "#레이": ["REI"],
    "#レイ": ["REI"],
    "#直井憐": ["REI"],
    "#JANGWONYOUNG": ["WONYOUNG"],
    "#WONYOUNG": ["WONYOUNG"],
    "#원영": ["WONYOUNG"],
    "#장원영": ["WONYOUNG"],
    "#ウォニョン": ["WONYOUNG"],
    "#LIZ": ["LIZ"],
    "#리즈": ["LIZ"],
    "#リズ": ["LIZ"],
    "#Liz": ["LIZ"],
    "#이서": ["LEESEO"],
    "#イソ": ["LEESEO"],
    "#LEESEO": ["LEESEO"],
    "#이현서": ["LEESEO"]
}


# 使用 lru_cache 裝飾器來優化性能
# lru_cache 會儲存函數的調用結果，避免重複計算
@lru_cache(maxsize=None)
def ive_tag_dict():
    return tag_dict


# 異步函數用於匹配輸入集合中的標籤
async def match_tags(input_set_to_search: set) -> set:
    """
    使用生成器表達式和集合推導式來高效地匹配標籤並返回匹配到的值的集合。

    參數:
    - input_set_to_search (set): 接受一個集合 input_set_to_search 作為輸入

    返回值:
    - set: 返回包含所有匹配 Discord 標籤的新集合
    """
    # 返回一個集合，集合中的元素是根據輸入集合中標籤匹配到的Discord值
    return {
        # 使用集合推導式構建匹配到的值的集合
        dict_value
        # 遍歷輸入集合中的每個標籤
        for tag in input_set_to_search
        # 檢查標籤 tag 是否存在於 ive_tag_dict 字典中
        if tag in ive_tag_dict()
        # 遍歷方式將所有匹配的 Discord 標籤添加到新的集合中
        for dict_value in ive_tag_dict()[tag]
    }
