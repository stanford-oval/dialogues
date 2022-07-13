from collections import defaultdict

import dictdiffer

from dialogues import Risawoz


def api_result_diff(knowledge, gold_knowledge):
    knowledge = dataset.span2knowledge(knowledge)
    processed_knowledge = defaultdict(dict)
    for d in gold_knowledge.keys():
        gold_knowledge[d] = {s: str(v) for s, v in gold_knowledge[d].items()}
    for d in knowledge.keys():
        for sv in knowledge[d]:
            processed_knowledge[d][sv['slot']] = str(sv['value'][0])
    return list(dictdiffer.diff(dict(processed_knowledge), gold_knowledge))


api_list = ["酒店", "旅游景点"]
dialogue_state = {
    "hotel": {'pricerange': {'relation': 'equal_to', 'value': ['偏贵']}, 'area': {'relation': 'equal_to', 'value': ['吴江']}},
    "attraction": {"name": {'relation': 'equal_to', 'value': ['金鸡湖景区']}},
}
src_lang = 'en_US'
knowledge = defaultdict(dict)

dataset = Risawoz()
new_knowledge_text, constraints = dataset.make_api_call(dialogue_state, knowledge, api_list, src_lang=src_lang)
gold_knowledge = {
    'hotel': {
        "name": "苏州黎里水岸寒舍精品酒店",
        "area": "吴江",
        "star": "5",
        "pricerange": "偏贵",
        "hotel_type": "商务出行",
        "room_type": "大床房",
        "parking": "免费",
        "room_charge": "629元",
        "address": "苏州吴江区黎里镇南新街5-9号",
        "phone_number": "180-5181-5602",
        "score": 4.6,
        "available_options": 4,
    },
    'attraction': {
        "name": "金鸡湖景区",
        "area": "工业园区",
        "type": "山水景区",
        "the_most_suitable_people": "情侣约会",
        "consumption": "偏贵",
        "metro_station": "是",
        "ticket_price": "免费",
        "phone_number": "400-7558558",
        "address": "苏州市工业园区星港街158号",
        "score": 4.5,
        "opening_hours": "全天",
        "features": "看东方之门等高楼，坐摩天轮，乘船夜游，感受苏州现代化的一面。",
        "available_options": 1,
    },
}

print('diff:', api_result_diff(new_knowledge_text, gold_knowledge))
