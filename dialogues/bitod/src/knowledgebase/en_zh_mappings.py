import json
import os
from collections import OrderedDict

from ...src.knowledgebase.hk_mtr import name_to_zh


def read_require_slots():
    require_slots = OrderedDict()
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for fn in os.listdir(os.path.join(cur_dir, "apis")):
        with open(os.path.join(cur_dir, "apis", fn)) as f:
            ontology = json.load(f)
            api_name = fn.replace(".json", "")

            if 'zh' in api_name:
                required = tuple(sorted([en2zh_SLOT_MAP[val] for val in ontology["required"]]))
            else:
                required = tuple(sorted(ontology["required"]))

            require_slots[api_name] = required
    require_slots['HKMTR zh'] = require_slots['HKMTR_en']
    return require_slots


zh2en_CARDINAL_MAP = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}
en2zh_CARDINAL_MAP = {v: k for k, v in zh2en_CARDINAL_MAP.items()}

en2zh_ACT_MAP = {
    'inform': "通知",
    'inform_intent': '告知意图',
    # both affirm and confirm are mapped to 确认  smh...
    "affirm": "确认",
    'confirm': "确认",
    'offer': "报价",
    'request': "要求",
    "request_more": "要求更多",
    "greeting": "问候",
    "thank_you": "谢谢你",
    "negate": "否定",
    "notify_success": "通知成功",
    "notify_fail": "通知失败",
    "goodbye": "再见",
    "request_update": "请求更新",
}
zh2en_ACT_MAP = {v: k for k, v in en2zh_ACT_MAP.items()}


en2zh_INTENT_MAP = {
    'inform': "通知",
    'confirm': "确认",
    'offer': "报价",
    'request': "要求",
    "request_more": "要求更多",
    "greeting": "问候",
    "affirm": "确认",
    "notify_success": "通知成功",
    "notify_fail": "通知失败",
    "goodbye": "再见",
    "request_update": "请求更新",
}
zh2en_INTENT_MAP = {v: k for k, v in en2zh_INTENT_MAP.items()}

zh2en_SLOT_MAP = {
    "意图": "intent",
    "名字": "name",
    "位置": "location",
    "评分": "rating",
    "类别": "type",
    "地址": "address",
    "电话": "phone_number",
    "可用选项": "available_options",
    "参考编号": "ref_number",
    "每晚价格": "price_per_night",
    "用户名": "user_name",
    "房间数": "number_of_rooms",
    "预订月": "start_month",
    "预订日": "start_day",
    "预订日期": "date",
    "预订天数": "number_of_nights",
    "价格范围": "price_level",
    "星级数": "stars",
    "菜品": "cuisine",
    "饮食限制": "dietary_restrictions",
    "日期": "day",
    "城市": "city",
    "最高温度": "max_temp",
    "最低温度": "min_temp",
    "天气": "weather",
    "描述": "description",
    "出发地": "departure",
    "目的地": "destination",
    "人数": "number_of_people",
    "时间": "time",
    # "日": "date",
    "预估时间": "estimated_time",
    "最短路线": "shortest_path",
    "价格": "price",
}

en2zh_SLOT_MAP = {v: k for k, v in zh2en_SLOT_MAP.items()}


en2zh_RELATION_MAP = {"equal_to": "等于", "not": "非", "less_than": "少于", "at_least": "至少", "one_of": "其中之一"}
zh2en_RELATION_MAP = {v: k for k, v in en2zh_RELATION_MAP.items()}

zh2en_SPECIAL_MAP = {"不在乎": "don't care"}
en2zh_SPECIAL_MAP = {v: k for k, v in zh2en_SPECIAL_MAP.items()}


# Mapping between api file names in kb/apis/* to a canonical name
zh2en_API_MAP = {
    "餐馆查询": "restaurants_zh_CN_search",
    "餐馆预订": "restaurants_zh_CN_booking",
    "宾馆查询": "hotels_zh_CN_search",
    "宾馆预订": "hotels_zh_CN_booking",
    "景点查询": "attractions_zh_CN_search",
    "天气查询": "weathers_zh_CN_search",
    "香港地铁": "HKMTR_zh",
}
en2zh_API_MAP = {v: k for k, v in zh2en_API_MAP.items()}


en_API_MAP = {
    'chat': 'chat',
    "restaurants_en_US_search": "restaurants search",
    "restaurants_en_US_booking": "restaurants booking",
    "hotels_en_US_search": "hotels search",
    "hotels_en_US_booking": "hotels booking",
    "attractions_en_US_search": "attractions search",
    "weathers_en_US_search": "weathers search",
    "HKMTR_en": "HKMTR en",
    "HKMTR_zh": "HKMTR zh",
}
r_en_API_MAP = {v: k for k, v in en_API_MAP.items()}

zh_API_MAP = {
    'chat': 'chat',
    "restaurants_zh_CN_search": "restaurants search",
    "restaurants_zh_CN_booking": "restaurants booking",
    "hotels_zh_CN_search": "hotels search",
    "hotels_zh_CN_booking": "hotels booking",
    "attractions_zh_CN_search": "attractions search",
    "weathers_zh_CN_search": "weathers search",
    "HKMTR_zh": "HKMTR zh",
}

zh_en_API_MAP = {
    "餐馆查询": "restaurants_en_US_search",
    "餐馆预订": "restaurants_en_US_booking",
    "宾馆查询": "hotels_en_US_search",
    "宾馆预订": "hotels_en_US_booking",
    "景点查询": "attractions_en_US_search",
    "天气查询": "weathers_en_US_search",
    "香港地铁": "HKMTR_en",
    "chat": "chat",
}
en_zh_API_MAP = {v: k for k, v in zh_en_API_MAP.items()}

API_MAP = {}
API_MAP.update(en_API_MAP)
API_MAP.update(en2zh_API_MAP)
API_MAP.update({k: k for k, v in zh2en_API_MAP.items()})
API_MAP.update({'HKMTR zh': 'HKMTR zh'})

# for cross lingual transfer
# mapping between slot values, not comprehensive, don't rely on it
cur_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cur_dir, "mappings/dict_en_zh.json")) as f:
    en2zh_VALUE_MAP = json.load(f)
    en2zh_VALUE_MAP.update(name_to_zh)
zh2en_VALUE_MAP = {v: k for k, v in en2zh_VALUE_MAP.items()}


# maps entities to their canonicalized version; api expects canonicalized version
# note entities in original and preprocessed datasets are not canonicalized;
cur_dir = os.path.dirname(os.path.abspath(__file__))
entity_map = {}
with open(os.path.join(cur_dir, "mappings/zh_entity_map.json")) as f:
    entity_map.update(json.load(f))
with open(os.path.join(cur_dir, "mappings/en_entity_map.json")) as f:
    entity_map.update(json.load(f))

reverse_entity_map = {v: k for k, v in entity_map.items()}

translation_dict = {
    **zh2en_SLOT_MAP,
    **zh2en_RELATION_MAP,
    **zh2en_INTENT_MAP,
    **zh2en_ACT_MAP,
    **zh2en_API_MAP,
    **zh2en_SPECIAL_MAP,
}
translation_dict["chat"] = "chat"
translation_dict = OrderedDict(sorted(translation_dict.items(), key=lambda item: len(item[0]), reverse=True))

required_slots = read_require_slots()
# mapping between api name and required slots to make an api call
required_slots = {API_MAP[k]: v for k, v in required_slots.items()}
api_names = list(required_slots.keys())
