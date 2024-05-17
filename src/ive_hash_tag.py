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
async def match_tags(input_set_to_search: set) -> str:
    # 初始化一個空集合來存儲匹配到的值
    matched_values = set()
    # 遍歷輸入集合中的每個標籤
    for tag in input_set_to_search:
        # 如果標籤在字典中，更新匹配到的值
        if tag in ive_tag_dict():
            matched_values.update(ive_tag_dict()[tag])
    return matched_values
