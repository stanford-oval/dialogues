import argparse
from collections import defaultdict

import dictdiffer

from dialogues import Risawoz

parser = argparse.ArgumentParser()
parser.add_argument("--setting", type=str, default="en", help="en, zh, en_zh, en2zh, zh2en")
args = parser.parse_args()


def api_result_diff(knowledge, gold_knowledge):
    knowledge = dataset.span2knowledge(knowledge)
    processed_knowledge = defaultdict(dict)
    for d in gold_knowledge.keys():
        gold_knowledge[d] = {s: str(v) for s, v in gold_knowledge[d].items()}
    for d in knowledge.keys():
        for sv in knowledge[d]:
            processed_knowledge[d][sv['slot']] = str(sv['value'][0])
    return list(dictdiffer.diff(dict(processed_knowledge), gold_knowledge))


api_list = ["hotel", "attraction"]

if args.setting == 'zh':
    dialogue_state = {
        "hotel": {'pricerange': {'relation': 'equal_to', 'value': ['偏贵']}, 'area': {'relation': 'equal_to', 'value': ['吴江']}},
        "attraction": {"name": {'relation': 'equal_to', 'value': ['金鸡湖景区']}},
    }
    gold_knowledge = {
        'hotel': {
            "name": "苏州黎里水岸寒舍精品酒店",
            "area": "吴江",
            "star": "5",
            "pricerange": "偏贵",
            "hotel_type": "商务出行",
            "room_type": "大床房",
            "parking": "免费",
            "room_charge": "629 元",
            "address": "苏州吴江区黎里镇南新街 5-9 号",
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
            "address": "苏州市工业园区星港街 158 号",
            "score": 4.5,
            "opening_hours": "全天",
            "features": "看东方之门等高楼，坐摩天轮，乘船夜游，感受苏州现代化的一面。",
            "available_options": 1,
        },
    }
elif args.setting == 'fr':
    dialogue_state = {
        "hotel": {
            'pricerange': {'relation': 'equal_to', 'value': ['un peu cher']},
            'area': {'relation': 'equal_to', 'value': ['District de Wujiang']},
        },
        "attraction": {"name": {'relation': 'equal_to', 'value': ['zone pittoresque du lac de Jinji']}},
    }
    gold_knowledge = {
        'hotel': {
            "name": "le petit hôtel de luxe Suzhou Shui'an Hanshe",
            "area": "District de Wujiang",
            "star": "5",
            "pricerange": "un peu cher",
            "hotel_type": "d'affaires",
            "room_type": "grande chambre",
            "parking": "gratuit",
            "room_charge": "629 yuans",
            "address": "n° 5-9, rue Nanxin, dans le village de Lili, dans le district de Wujiang, à Suzhou",
            "phone_number": "180-5181-5602",
            "score": "4,6",
            "available_options": 4,
        },
        'attraction': {
            "name": "zone pittoresque du lac de Jinji",
            "area": "Parc industriel de Suzhou",
            "type": "endroit",
            "the_most_suitable_people": "rencontres",
            "consumption": "un peu cher",
            "metro_station": "true",
            "ticket_price": "gratuit",
            "phone_number": "400-7558558",
            "address": "n° 158 de la rue Xinggang, dans le parc industriel de Suzhou, dans la ville de Suzhou",
            "score": "4,5",
            "opening_hours": "toute la journée",
            "features": "Vous aurez une bonne vue sur les grands bâtiments comme la Porte de l'Orient, vous pourrez monter sur la grande roue, faire une croisière de nuit et découvrir le côté moderne de Suzhou.",
            "available_options": 1,
        },
    }

elif args.setting == 'en':
    dialogue_state = {
        "hotel": {
            'pricerange': {'relation': 'equal_to', 'value': ['slightly expensive']},
            'area': {'relation': 'equal_to', 'value': ['Wujiang District']},
        },
        "attraction": {"name": {'relation': 'equal_to', 'value': ['Jinji Lake Scenic Area']}},
    }
    gold_knowledge = {
        'hotel': {
            "name": "Suzhou Shui'an Hanshe Boutique Hotel",
            "area": "Wujiang District",
            "star": "5",
            "pricerange": "slightly expensive",
            "hotel_type": "business",
            "room_type": "king-size room",
            "parking": "free",
            "room_charge": "629 yuan",
            "address": "No. 5-9, Nanxin Street, Lili Town, Wujiang District, Suzhou",
            "phone_number": "180-5181-5602",
            "score": "4.6",
            "available_options": 4,
        },
        'attraction': {
            "name": "Jinji Lake Scenic Area",
            "area": "Suzhou Industrial Park",
            "type": "landscape scenic spot",
            "the_most_suitable_people": "dating",
            "consumption": "slightly expensive",
            "metro_station": "true",
            "ticket_price": "free",
            "phone_number": "400-7558558",
            "address": "No.158, Xinggang Street, Suzhou Industrial Park, Suzhou City",
            "score": "4.5",
            "opening_hours": "all day",
            "features": "get a good view of tall buildings like the Gate of the Orient, ride the Ferris wheel, take a night cruise, and feel the modern side of Suzhou.",
            "available_options": 1,
        },
    }
elif args.setting == 'enhi':
    dialogue_state = {
        "hotel": {
            'pricerange': {'relation': 'equal_to', 'value': ['slightly expensive']},
            'area': {'relation': 'equal_to', 'value': ['वुजियांग जिले']},
        },
        "attraction": {"name": {'relation': 'equal_to', 'value': ['Jinji Lake Scenic Area']}},
    }
    gold_knowledge = {
        'hotel': {
            "name": "Suzhou Shui'an Hanshe Boutique Hotel",
            "area": "वुजियांग जिले",
            "star": "5",
            "pricerange": "slightly expensive",
            "hotel_type": "business",
            "room_type": "king-size room",
            "parking": "free",
            "room_charge": "629 yuan",
            "address": "No. 5-9, Nanxin Street, Lili Town, Wujiang District, Suzhou",
            "phone_number": "180-5181-5602",
            "score": "4.6",
            "available_options": 4,
        },
        'attraction': {
            "name": "Jinji Lake Scenic Area",
            "area": "Suzhou Industrial Park",
            "type": "landscape scenic spot",
            "the_most_suitable_people": "dating",
            "consumption": "slightly expensive",
            "metro_station": "true",
            "ticket_price": "free",
            "phone_number": "400-7558558",
            "address": "जिंगगैंग स्ट्रीट , सूज़ौ इंडस्ट्रियल पार्क , सूज़ौ सिटी",
            "score": "4.5",
            "opening_hours": "all day",
            "features": "get a good view of tall buildings like the Gate of the Orient, ride the Ferris wheel, take a night cruise, and feel the modern side of Suzhou.",
            "available_options": 1,
        },
    }
elif args.setting == 'hi':
    dialogue_state = {
        "hotel": {
            'pricerange': {'relation': 'equal_to', 'value': ['थोड़ा महंगा']},
            'area': {'relation': 'equal_to', 'value': ['वुजियांग जिले']},
        },
        "attraction": {"name": {'relation': 'equal_to', 'value': ['जिनजी झील दर्शनीय क्षेत्र']}},
    }
    gold_knowledge = {
        'hotel': {
            "name": "सूज़ौ शुआन हंसे बुटीक होटल",
            "area": "वुजियांग जिले",
            "star": "5-स्टार",
            "pricerange": "थोड़ा महंगा",
            "hotel_type": "बिजनेस",
            "room_type": "बड़ा आकार के कमरे",
            "parking": "मुफ्त",
            "room_charge": "629 युआन",
            "address": "नंबर 5-9, नानक्सिन स्ट्रीट, लिली टाउन, वुजियांग जिला, सूज़ौ",
            "phone_number": "180-5181-5602",
            "score": "4.6",
            "available_options": 4,
        },
        'attraction': {
            "name": "जिनजी झील दर्शनीय क्षेत्र",
            "area": "सूज़ौ औद्योगिक पार्क",
            "type": "लैंडस्केप दर्शनीय स्थल",
            "the_most_suitable_people": "डेटिंग",
            "consumption": "थोड़ा महंगा",
            "metro_station": "true",
            "ticket_price": "मुफ्त",
            "phone_number": "400-7558558",
            "address": "158, जिंगगैंग स्ट्रीट, सूज़ौ इंडस्ट्रियल पार्क, सूज़ौ सिटी",
            "score": "4.5",
            "opening_hours": "पूरे दिन",
            "features": "get a good view of tall buildings like the Gate of the Orient, ride the Ferris wheel, take a night cruise, and feel the modern side of Suzhou.",
            "available_options": 1,
        },
    }

elif args.setting == 'ko':
    dialogue_state = {
        "hotel": {
            'pricerange': {'relation': 'equal_to', 'value': ['조금 비쌉니다']},
            'area': {'relation': 'equal_to', 'value': ['우장구']},
        },
        "attraction": {"name": {'relation': 'equal_to', 'value': ['진지 호수 풍경구']}},
    }
    gold_knowledge = {
        'hotel': {
            "name": "쑤저우 쉬안 한슈 부티크 호텔",
            "area": "우장구",
            "star": "5",
            "pricerange": "조금 비쌉니다",
            "hotel_type": "비즈니스",
            "room_type": "킹사이즈 객실",
            "parking": "무료",
            "room_charge": "629위안",
            "address": "쑤저우시 우장구 릴리 마을 난씬가 5-9호",
            "phone_number": "180-5181-5602",
            "score": "4.6",
            "available_options": 4
        },
        'attraction': {
            "name": "진지 호수 풍경구",
            "area": "쑤저우 공업원구",
            "type": "풍경이 좋은 곳",
            "the_most_suitable_people": "데이트",
            "consumption": "조금 비싼",
            "metro_station": "있음",
            "ticket_price": "무료",
            "phone_number": "400-7558558",
            "address": "쑤저우시 쑤저우 공업원구 신강가 158호",
            "score": "4.5점",
            "opening_hours": "하루 종일",
            "features": "동방지문과 같은 높은 건물들의 아름다운 전경을 보거나, 관람차나 야간 유람선을 타면서 쑤저우의 현대적인 면을 느낄 수 있습니다.",
            "available_options": 1
        },
    }


knowledge = defaultdict(dict)

dataset = Risawoz()
new_knowledge_text, constraints = dataset.make_api_call(dialogue_state, knowledge, api_list, src_lang=args.setting)

api_diff = api_result_diff(new_knowledge_text, gold_knowledge)
print('diff:', api_diff)
assert len(api_diff) == 0
