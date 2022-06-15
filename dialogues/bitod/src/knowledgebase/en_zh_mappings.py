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


zh2en_DAY_MAP = {
    "星期一": "Monday",
    "星期二": "Tuesday",
    "星期三": "Wednesday",
    "星期四": "Thursday",
    "星期五": "Friday",
    "星期六": "Saturday",
    "星期天": "Sunday",
}
en2zh_DAY_MAP = {v: k for k, v in zh2en_DAY_MAP.items()}


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

ENGLISH_MONTH_MAPPING = {
    '1': 'January',
    '2': 'February',
    '3': 'March',
    '4': 'April',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August',
    '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
}
MONTH_MAPPING_EN = {
    k + ' month': v for k, v in sorted(ENGLISH_MONTH_MAPPING.items(), key=lambda item: int(item[0]), reverse=True)
}
MONTH_MAPPING_ZH = {
    v + '月': k + '月' for k, v in sorted(ENGLISH_MONTH_MAPPING.items(), key=lambda item: int(item[0]), reverse=True)
}

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
    map_dict = json.load(f)

en2zh_VALUE_MAP = name_to_zh
en2zh_VALUE_MAP.update(map_dict)

zh2en_VALUE_MAP = {v: k for k, v in name_to_zh.items()}
zh2en_VALUE_MAP.update({v: k for k, v in map_dict.items()})


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


# google translated
zh2en_missing_mapping = {
    "吕奉先": "Lu Fengxian",
    "孙念祖": "Sun Nianzu",
    "关玉和": "Guan Yuhe",
    "安怡孙": "An Yi Sun",
    "范长江": "Fan Changjiang",
    "刘永生": "Liu Yongsheng",
    "郑义": "Zheng Yi",
    "吴家栋": "Wu Jiadong",
    "罗元发": "Luo Yuanfa",
    "张志远": "Zhang Zhiyuan",
    "李大江": "Li Dajiang",
    "李秉贵": "Li Binggui",
    "赵德茂": "Zhao Demao",
    "吴立功": "Wu Ligong",
    "赵进喜": "Zhao Jinxi",
    "汤念祖": "Tang Nianzu",
    "马宏宇": "Ma Hongyu",
    "洪学智": "Hong Xuezhi",
    "伊斯坦堡快餐": "fast food in istanbul",
    "马连良": "Ma Lianliang",
    "谢大海": "Xie Dahai",
    "吴克俭": "Wu Kejian",
    "张国柱": "Zhang Guozhu",
    "年广嗣": "Nian Guangsi",
    "何光宗": "He Guangzong",
    "彭万里": "Peng Wanli",
    "李宗仁": "Li Zongren",
    "赵大华": "Zhao Dahua",
    "马建国": "Ma Jianguo",
    "高尚德": "noble",
    "钱汉祥": "Qian Hanxiang",
    "王子久": "prince long",
    "冯兴国": "Feng Xingguo",
    "刘长胜": "Liu Changsheng",
    "吕文达": "Lu Wenda",
    "冷德友": "Leng Deyou",
    "刘造时": "Liu Zaoshi",
    "孙顺达": "Sun Shunda",
    "胡宝善": "Hu Baoshan",
    "张石山": "Zhang Shishan",
    "吕德榜": "Ludbang",
    "李四光": "Li Siguang",
    "李开富": "Li Kaifu",
    "蔡德霖": "Cai Delin",
    "林君雄": "Lin Junxiong",
    "杨惟义": "Yang Weiyi",
    "李书诚": "Li Shucheng",
    "朱希亮": "Zhu Xiliang",
    "王德茂": "Wang Demao",
    "孙应吉": "Sun Yingji",
    "宗敬先": "Zong Jingxian",
    "city花园": "city garden",
    "程孝先": "Cheng Xiaoxian",
    "杨勇": "Yang Yong",
    "钱运高": "Qian Yungao",
    "贾德善": "Jia Deshan",
    "高大山": "high mountain",
    "李际泰": "Li Jitai",
    "刘乃超": "Liu Naichao",
    "张成基": "Zhang Chengji",
    "贾怡": "Jia Yi",
    "节振国": "Jie Zhenguo",
    "city花园酒店": "city Garden Hotel",
    "张伍绍祖": "Zhang Wu Shaozu",
    "孙寿康": "Sun Shoukang",
    "-11": "-11",
    "张广才": "Zhang Guangcai",
    "王海": "Wang Hai",
    "谭平山": "Tan Pingshan",
    "孙天民": "Sun Tianmin",
    "余克勤": "Yu Keqin",
    "not洲料理": "not continental cuisine",
    "钱生禄": "Qian Shenglu",
    "马继祖": "Ma Jizu",
    "新city中央广场": "new city central plaza",
    "-6": "-6",
    "章汉夫": "Zhang Hanfu",
    "刁富贵": "Diao Fugui",
    "关仁": "Guan Ren",
    "汤绍箕": "Tang Shaoji",
    "郝爱民": "Hao Aimin",
    "王仁兴": "Wang Renxing",
    "吴国梁": "Wu Guoliang",
}

en2zh_missing_mapping = {
    "David": "大卫",
    "Michael": "迈克尔",
    "None": "没有任何",
    "Anthony": "安东尼",
    "Danielle": "丹妮尔",
    "Rachel": "雷切尔",
    "Mary": "玛丽",
    "Joyce": "乔伊斯",
    "William": "威廉",
    "Haipohong Road Temporary Market": "海浦红路临时市场",
    "Kelly": "凯利",
    "Brandon": "布兰登",
    "Noah": "诺亚",
    "Ann": "安",
    "Stephanie": "斯蒂芬妮",
    "Cheryl": "谢丽尔",
    "Kimberly": "金佰利",
    "Samuel": "塞缪尔",
    "Andrew": "安德鲁",
    "Steven": "史蒂文",
    "Johnny": "约翰尼",
    "Gary": "加里",
    "Carl": "卡尔",
    "Richard": "理查德",
    "Kayla": "凯拉",
    "Linda": "琳达",
    "Concept by SAAM": "SAAM 的概念",
    "Matthew": "马修",
    "Victoria": "维多利亚",
    "Jacqueline": "杰奎琳",
    "Gerald": "杰拉德",
    "Rose": "玫瑰",
    "Terry": "特里",
    "Christine": "克里斯汀",
    "Heather": "希瑟",
    "Karen": "凯伦",
    "Jesse": "杰西",
    "Alan": "艾伦",
    "Harold": "哈罗德",
    "Jack": "杰克",
    "Eric": "埃里克",
    "Sarah": "莎拉",
    "Joan": "琼",
    "Kathryn": "凯瑟琳",
    "Megan": "梅根",
    "Jonathan": "乔纳森",
    "Diana": "戴安娜",
    "Dennis": "丹尼斯",
    "Russell": "罗素",
    "Vincent": "文森特",
    "Judy": "朱迪",
    "Bobby": "鲍比",
    "Nicholas": "尼古拉斯",
    "Susan": "苏珊",
    "Lauren": "劳伦",
    "Samantha": "萨曼莎",
    "Scott": "斯科特",
    "Nathan": "弥敦道",
    "Sean": "肖恩",
    "86 2477 4896": "86 2477 4896",
    "James": "詹姆士",
    "Peter": "彼得",
    "Paul": "保罗",
    "Judith": "朱迪思",
    "Thomas": "托马斯",
    "Cynthia": "辛西娅",
    "Timothy": "提摩太",
    "Alice": "爱丽丝",
    "Gabriel": "加布里埃尔",
    "Joshua": "约书亚",
    "Shirley": "雪莉",
    "Lawrence": "劳伦斯",
    "Joseph": "约瑟夫",
    "Janet": "珍妮特",
    "Ralph": "拉尔夫",
    "Virginia": "弗吉尼亚",
    "Lisa": "丽莎",
    "Marilyn": "玛丽莲",
    "Keith": "基思",
    "Charlotte": "夏洛特",
    "Diane": "黛安",
    "Justin": "贾斯汀",
    "Helen": "海伦",
    "Aaron": "亚伦",
    "Bruce": "布鲁斯",
    "Carol": "颂歌",
    "Douglas": "道格拉斯",
    "Evelyn": "伊芙琳",
    "Charles": "查尔斯",
    "Abigail": "阿比盖尔",
    "Willie": "威利",
    "Deborah": "黛博拉",
    "Kathleen": "凯瑟琳",
    "Nicole": "妮可",
    "Joe": "乔",
    "Edward": "爱德华",
    "Stephen": "斯蒂芬",
    "Jessica": "杰西卡",
    "Benjamin": "本杰明",
    "Frank": "坦率",
    "Mark": "标记",
    "Andrea": "安德烈亚",
    "Marie": "玛丽",
    "Christopher": "克里斯托弗",
    "Hong Kong Tourism Board, Hong Kong Island Visitor Centre": "香港旅游发展局港岛游客中心",
    "Juan": "胡安",
    "Ruth": "露丝",
    "Anna": "安娜",
    "Jennifer": "珍妮弗",
    "Brenda": "布伦达",
    "Arthur": "亚瑟",
    "Frances": "弗朗西丝",
    "Alexander": "亚历山大",
    "Grace": "优雅",
    "George": "乔治",
    "Doris": "多丽丝",
    "Wayne": "韦恩",
    "Carolyn": "卡罗琳",
    "Betty": "贝蒂",
    "Donald": "唐纳德",
    "Jose": "何塞",
    "Billy": "比利",
    "Walter": "沃尔特",
    "Alexis": "亚历克西斯",
    "Dorothy": "多萝西",
    "Denise": "丹妮丝",
    "Ronald": "罗纳德",
    "Hannah": "汉娜",
    "Kyle": "凯尔",
    "Bradley": "布拉德利",
    "Jeffrey": "杰弗里",
    "Kenneth": "肯尼斯",
    "Martha": "玛莎",
    "Katherine": "凯瑟琳",
    "Jordan": "约旦",
    "Sara": "萨拉",
    "Olivia": "奥利维亚",
}
