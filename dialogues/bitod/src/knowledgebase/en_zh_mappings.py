import json
import os
from collections import OrderedDict

from dialogues.bitod.src.knowledgebase.hk_mtr import name_to_zh


class BitodMapping(object):
    def __init__(self):

        self.en2zh_RELATION_MAP = {"equal_to": "等于", "not": "非", "less_than": "少于", "at_least": "至少", "one_of": "其中之一"}
        self.zh2en_RELATION_MAP = {v: k for k, v in self.en2zh_RELATION_MAP.items()}

        self.zh2en_SPECIAL_MAP = {"不在乎": "don't care"}
        self.en2zh_SPECIAL_MAP = {v: k for k, v in self.zh2en_SPECIAL_MAP.items()}

        # TODO: missing
        self.DOMAIN_SLOT_MAP = {}

        self.zh2en_DOMAIN_MAP = {
            # currently untranslated
            "天气": "weather",
            "火车": "train",
            "电脑": "pc",
            "电影": "movie",
            "辅导班": "class",
            "汽车": "car",
            "餐厅": "restaurant",
            "酒店": "hotel",
            "旅游景点": "attraction",
            "飞机": "flight",
            "医院": "hospital",
            "电视剧": "tv",
            "通用": "general",
        }
        self.en2zh_DOMAIN_MAP = {v: k for k, v in self.zh2en_DOMAIN_MAP.items()}

        self.en2zh_ACT_MAP = {
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
        self.zh2en_ACT_MAP = {v: k for k, v in self.en2zh_ACT_MAP.items()}

        self.zh2en_SLOT_MAP = {
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
        self.en2zh_SLOT_MAP = {v: k for k, v in self.zh2en_SLOT_MAP.items()}

        # for cross lingual transfer
        # mapping between slot values, not comprehensive, don't rely on it
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cur_dir, "mappings/dict_en_zh.json")) as f:
            map_dict = json.load(f)

        en2zh_VALUE_MAP = name_to_zh
        en2zh_VALUE_MAP.update(map_dict)
        self.en2zh_VALUE_MAP = en2zh_VALUE_MAP

        zh2en_VALUE_MAP = {v: k for k, v in name_to_zh.items()}
        zh2en_VALUE_MAP.update({v: k for k, v in map_dict.items()})
        self.zh2en_VALUE_MAP = zh2en_VALUE_MAP

        # maps entities to their canonicalized version; api expects canonicalized version
        # note entities in original and preprocessed datasets are not canonicalized;
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        entity_map = {}
        with open(os.path.join(cur_dir, "mappings/zh_entity_map.json")) as f:
            entity_map.update(json.load(f))
        with open(os.path.join(cur_dir, "mappings/en_entity_map.json")) as f:
            entity_map.update(json.load(f))
        self.entity_map = entity_map

        self.reverse_entity_map = {v: k for k, v in self.entity_map.items()}

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cur_dir, "mappings/zh2en_missing.json")) as f:
            self.zh2en_missing_MAP = json.load(f)
        with open(os.path.join(cur_dir, "mappings/en2zh_missing.json")) as f:
            self.en2zh_missing_MAP = json.load(f)

        # Mapping between api file names in kb/apis/* to a canonical name
        self.zh2en_API_MAP = {
            "餐馆查询": "restaurants_zh_CN_search",
            "餐馆预订": "restaurants_zh_CN_booking",
            "宾馆查询": "hotels_zh_CN_search",
            "宾馆预订": "hotels_zh_CN_booking",
            "景点查询": "attractions_zh_CN_search",
            "天气查询": "weathers_zh_CN_search",
            "香港地铁": "HKMTR_zh",
        }
        self.en2zh_API_MAP = {v: k for k, v in self.zh2en_API_MAP.items()}

        self.zh2en_INTENT_MAP = {
            "餐馆查询": "restaurants search",
            "餐馆预订": "restaurants booking",
            "宾馆查询": "hotels search",
            "宾馆预订": "hotels booking",
            "景点查询": "attractions search",
            "天气查询": "weathers search",
            "香港地铁": "HKMTR en",
        }
        self.en2zh_INTENT_MAP = {v: k for k, v in self.zh2en_INTENT_MAP.items()}

        self.en_API_MAP = {
            'chat': 'chat',
            "restaurants_en_US_search": "restaurants search",
            "restaurants_en_US_booking": "restaurants booking",
            "hotels_en_US_search": "hotels search",
            "hotels_en_US_booking": "hotels booking",
            "attractions_en_US_search": "attractions search",
            "weathers_en_US_search": "weathers search",
            "HKMTR_en": "HKMTR en",
        }
        self.r_en_API_MAP = {v: k for k, v in self.en_API_MAP.items()}

        self.zh_API_MAP = {
            'chat': 'chat',
            "restaurants_zh_CN_search": "restaurants search",
            "restaurants_zh_CN_booking": "restaurants booking",
            "hotels_zh_CN_search": "hotels search",
            "hotels_zh_CN_booking": "hotels booking",
            "attractions_zh_CN_search": "attractions search",
            "weathers_zh_CN_search": "weathers search",
            "HKMTR_zh": "HKMTR en",
        }

        self.zh_en_API_MAP = {
            "餐馆查询": "restaurants_en_US_search",
            "餐馆预订": "restaurants_en_US_booking",
            "宾馆查询": "hotels_en_US_search",
            "宾馆预订": "hotels_en_US_booking",
            "景点查询": "attractions_en_US_search",
            "天气查询": "weathers_en_US_search",
            "香港地铁": "HKMTR_en",
            "chat": "chat",
        }
        self.en_zh_API_MAP = {v: k for k, v in self.zh_en_API_MAP.items()}

        API_MAP = {}
        API_MAP.update(self.en_API_MAP)
        API_MAP.update(self.en2zh_API_MAP)
        API_MAP.update({k: k for k, v in self.zh2en_API_MAP.items()})
        API_MAP.update({'HKMTR zh': 'HKMTR zh'})

        self.API_MAP = API_MAP

        translation_dict = {
            **self.zh2en_API_MAP,
            **self.zh2en_DOMAIN_MAP,
            **self.zh2en_SLOT_MAP,
            **self.zh2en_ACT_MAP,
            **self.zh2en_RELATION_MAP,
            **self.zh2en_SPECIAL_MAP,
        }
        translation_dict["chat"] = "chat"
        self.translation_dict = OrderedDict(sorted(translation_dict.items(), key=lambda item: len(item[0]), reverse=True))

        required_slots = self.read_require_slots()
        self.required_slots = {self.API_MAP[k]: v for k, v in required_slots.items()}
        self.api_names = list(self.required_slots.keys())

        self.skip_slots_for_kb = ["type", "description", "类别", "描述"]

    def read_require_slots(self):
        require_slots = OrderedDict()
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        for fn in os.listdir(os.path.join(cur_dir, "apis")):
            with open(os.path.join(cur_dir, "apis", fn)) as f:
                ontology = json.load(f)
                api_name = fn.replace(".json", "")
                required = tuple(sorted(ontology["required"]))
                if 'zh' in api_name:
                    require_slots[api_name] = [self.en2zh_SLOT_MAP[val] for val in required]
                else:
                    require_slots[api_name] = required

        require_slots['HKMTR zh'] = require_slots['HKMTR_en']

        return require_slots
