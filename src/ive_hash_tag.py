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


@lru_cache(maxsize=None)
def ive_tag_dict():
    return tag_dict


async def match_tags(input_set_to_search: set) -> str:
    matched_values = set()
    for tag in input_set_to_search:
        if tag in ive_tag_dict():
            matched_values.update(ive_tag_dict()[tag])
    return matched_values
