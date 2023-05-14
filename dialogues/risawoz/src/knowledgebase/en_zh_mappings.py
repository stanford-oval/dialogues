import json
import os
from collections import OrderedDict, defaultdict


class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            return self.default_factory(key)


class RisawozMapping(object):
    def __init__(self, src='zh', tgt='en'):
        self.src = src
        self.tgt = tgt
        # currently untranslated
        self.API_MAP = keydefaultdict(lambda k: k)
        self.zh_API_MAP = keydefaultdict(lambda k: k)
        self.en_API_MAP = keydefaultdict(lambda k: k)
        self.zh_en_API_MAP = keydefaultdict(lambda k: k)

        self.entity_map = keydefaultdict(lambda k: k)
        self.reverse_entity_map = keydefaultdict(lambda k: k)

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cur_dir, f"mappings/{tgt}2canonical.json")) as f:
            en2canonical_tmp = json.load(f)
        en2canonical = {}
        rev_en2canonical = {}
        for domain, items in en2canonical_tmp.items():
            for slot, values in items.items():
                for canon, vals in values.items():
                    rev_en2canonical[canon] = vals
                    if isinstance(vals, list):
                        for val in vals:
                            en2canonical[val] = canon
                    else:
                        assert isinstance(vals, str)
                        en2canonical[vals] = canon
        self.en2canonical = en2canonical
        self.rev_en2canonical = rev_en2canonical

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(cur_dir, f"mappings/{src}2{tgt}_alignment.json")):
            with open(os.path.join(cur_dir, f"mappings/{src}2{tgt}_alignment.json")) as f:
                zh2en_alignment = json.load(f)
            zh2en_value = {}
            for domain, items in zh2en_alignment.items():
                for slot, values in items.items():
                    for zh_val, en_val in values.items():
                        zh2en_value[zh_val] = en_val
        else:
            with open(os.path.join(cur_dir, f"mappings/{src}2en_alignment.json")) as f:
                src2en_alignment = json.load(f)
                src2en_value = {}
                for domain, items in src2en_alignment.items():
                    for slot, values in items.items():
                        for src_val, en_val in values.items():
                            src2en_value[src_val] = en_val
            with open(os.path.join(cur_dir, f"mappings/en2{tgt}_alignment.json")) as f:
                en2tgt_alignment = json.load(f)
                en2tgt_value = {}
                for domain, items in en2tgt_alignment.items():
                    for slot, values in items.items():
                        for en_val, tgt_val in values.items():
                            en2tgt_value[en_val] = tgt_val

            zh2en_value = {}
            for k, v in src2en_value.items():
                zh2en_value[k] = en2tgt_value.get(v, v)

        self.zh2en_VALUE_MAP = zh2en_value
        self.en2zh_VALUE_MAP = {v: k for k, v in self.zh2en_VALUE_MAP.items()}

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cur_dir, "mappings/zh2en_missing.json")) as f:
            self.zh2en_missing_MAP = json.load(f)

        with open(os.path.join(cur_dir, "mappings/zh2fr_missing.json")) as f:
            self.zh2fr_missing_MAP = json.load(f)

        with open(os.path.join(cur_dir, "mappings/zh2hi_missing.json")) as f:
            self.zh2hi_missing_MAP = json.load(f)

        with open(os.path.join(cur_dir, "mappings/zh2ko_missing.json")) as f:
            self.zh2ko_missing_MAP = json.load(f)

        # self.zh2en_missing_MAP = keydefaultdict(lambda k: k)

        self.en2zh_missing_MAP = keydefaultdict(lambda k: k)

        self.en2zh_RELATION_MAP = {"equal_to": "等于", "not": "非", "less_than": "少于", "at_least": "至少", "one_of": "其中之一"}
        self.zh2en_RELATION_MAP = {v: k for k, v in self.en2zh_RELATION_MAP.items()}

        self.zh2en_SPECIAL_MAP = {"不在乎": "don't care"}
        self.en2zh_SPECIAL_MAP = {v: k for k, v in self.zh2en_SPECIAL_MAP.items()}

        # TODO: this mapping should only include slots that are required to make an api call for the domain. It should not include all the slots.
        self.DOMAIN_SLOT_MAPS = {
            "zh": {
                '医院': [
                    '区域',
                    '名称',
                    '门诊时间',
                    '挂号时间',
                    'DSA',
                    '3.0T MRI',
                    '重点科室',
                    '电话',
                    '公交线路',
                    '地铁可达',
                    'CT',
                    '等级',
                    '性质',
                    '类别',
                    '地址',
                ],
                '天气': ['温度', '目的地', '日期', '城市', '风力风向', '天气', '紫外线强度'],
                '旅游景点': [
                    '门票价格',
                    '电话号码',
                    '菜系',
                    '名称',
                    '评分',
                    '最适合人群',
                    '房费',
                    '景点类型',
                    '房型',
                    '推荐菜',
                    '消费',
                    '开放时间',
                    '价位',
                    '是否地铁直达',
                    '区域',
                    '地址',
                    '特点',
                ],
                '汽车': [
                    '座椅通风',
                    '油耗水平',
                    '级别',
                    '能源类型',
                    '名称',
                    '价格',
                    '驱动方式',
                    '所属价格区间',
                    '车型',
                    '座位数',
                    '座椅加热',
                    '倒车影像',
                    '定速巡航',
                    '动力水平',
                    '车系',
                    '厂商',
                ],
                '火车': ['出发时间', '票价', '目的地', '车型', '舱位档次', '日期', '时长', '到达时间', '车次信息', '出发地', '准点率', '航班信息', '坐席'],
                '电影': ['制片国家/地区', '豆瓣评分', '片名', '主演名单', '具体上映时间', '导演', '片长', '类型', '年代', '主演'],
                '电脑': [
                    '价格区间',
                    '内存容量',
                    '商品名称',
                    '显卡型号',
                    '裸机重量',
                    '价格',
                    '品牌',
                    '系统',
                    'CPU型号',
                    '系列',
                    '特性',
                    '屏幕尺寸',
                    '游戏性能',
                    '分类',
                    '产品类别',
                    '待机时长',
                    '色系',
                    '硬盘容量',
                    'CPU',
                    '显卡类别',
                ],
                '电视剧': ['制片国家/地区', '豆瓣评分', '片名', '主演名单', '首播时间', '导演', '片长', '集数', '单集片长', '类型', '年代', '主演'],
                '辅导班': [
                    '开始日期',
                    '教师',
                    '上课方式',
                    '校区',
                    '价格',
                    '难度',
                    '时段',
                    '课时',
                    '科目',
                    '班号',
                    '结束日期',
                    '年级',
                    '下课时间',
                    '教室地点',
                    '每周',
                    '课次',
                    '上课时间',
                    '区域',
                ],
                '酒店': ['电话号码', '星级', '名称', '房费', '地址', '地铁是否直达', '房型', '停车场', '推荐菜', '酒店类型', '价位', '是否地铁直达', '区域', '评分'],
                '飞机': ['出发时间', '票价', '温度', '目的地', '起飞时间', '舱位档次', '日期', '城市', '到达时间', '出发地', '准点率', '航班信息', '天气'],
                '餐厅': ['营业时间', '电话号码', '菜系', '名称', '评分', '房费', '人均消费', '推荐菜', '开放时间', '价位', '是否地铁直达', '区域', '地址'],
                '通用': [],
            },
            "en": {
                'hospital': [
                    'area',
                    'name',
                    'service_time',
                    'registration_time',
                    'DSA',
                    '3.0T_MRI',
                    'key_departments',
                    'phone',
                    'bus_routes',
                    'metro_station',
                    'CT',
                    'level',
                    'public_or_private',
                    'general_or_specialized',
                    'address',
                ],
                'weather': ['temperature', 'destination', 'date', 'city', 'wind', 'weather_condition', 'UV_intensity'],
                'attraction': [
                    'ticket_price',
                    'phone_number',
                    'cuisine',
                    'name',
                    'score',
                    'the_most_suitable_people',
                    'room_charge',
                    'type',
                    'room_type',
                    'dishes',
                    'consumption',
                    'opening_hours',
                    'pricerange',
                    'metro_station',
                    'area',
                    'address',
                    'features',
                ],
                'car': [
                    'ventilated_seats',
                    'fuel_consumption',
                    'size',
                    'hybrid',
                    'name',
                    'price',
                    '4WD',
                    'pricerange',
                    'classification',
                    'number_of_seats',
                    'heated_seats',
                    'parking_assist_system',
                    'cruise_control_system',
                    'power_level',
                    'series',
                    'brand',
                ],
                'train': [
                    'departure_time',
                    'ticket_price',
                    'destination',
                    'classification',
                    'class_cabin',
                    'date',
                    'duration',
                    'arrival_time',
                    'train_number',
                    'departure',
                    'punctuality_rate',
                    'flight_information',
                    'seat_type',
                ],
                'movie': [
                    'production_country_or_area',
                    'Douban_score',
                    'title',
                    'name_list',
                    'release_date',
                    'director',
                    'film_length',
                    'type',
                    'decade',
                    'star',
                ],
                'pc': [
                    'pricerange',
                    'memory_capacity',
                    'product_name',
                    'GPU_model',
                    'weight',
                    'price',
                    'brand',
                    'operating_system',
                    'CPU_model',
                    'series',
                    'screen_size',
                    'game_performance',
                    'usage',
                    'computer_type',
                    'standby_time',
                    'colour',
                    'hard_disk_capacity',
                    'CPU',
                    'GPU_category',
                ],
                'tv': [
                    'production_country_or_area',
                    'Douban_score',
                    'title',
                    'name_list',
                    'premiere_time',
                    'director',
                    'film_length',
                    'episodes',
                    'episode_length',
                    'type',
                    'decade',
                    'star',
                ],
                'class': [
                    'start_date',
                    'teacher',
                    'type',
                    'campus',
                    'price',
                    'level',
                    'time',
                    'hours',
                    'subject',
                    'class_number',
                    'end_date',
                    'grade',
                    'end_time',
                    'classroom',
                    'day',
                    'times',
                    'start_time',
                    'area',
                ],
                'hotel': [
                    'phone_number',
                    'star',
                    'name',
                    'room_charge',
                    'address',
                    'metro_station',
                    'room_type',
                    'parking',
                    'dishes',
                    'hotel_type',
                    'pricerange',
                    'metro_station',
                    'area',
                    'score',
                ],
                'flight': [
                    'departure_time',
                    'ticket_price',
                    'temperature',
                    'destination',
                    'departure_time',
                    'class_cabin',
                    'date',
                    'city',
                    'arrival_time',
                    'departure',
                    'punctuality_rate',
                    'flight_information',
                    'weather_condition',
                ],
                'restaurant': [
                    'business_hours',
                    'phone_number',
                    'cuisine',
                    'name',
                    'score',
                    'room_charge',
                    'per_capita_consumption',
                    'dishes',
                    'opening_hours',
                    'pricerange',
                    'metro_station',
                    'area',
                    'address',
                ],
                'general': [],
            },
        }
        self.DOMAIN_SLOT_MAP = self.DOMAIN_SLOT_MAPS[src]

        self.zh2en_DOMAIN_MAPS = {
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
        self.zh2en_DOMAIN_MAP = self.zh2en_DOMAIN_MAPS
        self.en2zh_DOMAIN_MAP = {v: k for k, v in self.zh2en_DOMAIN_MAP.items()}

        self.zh2en_INTENT_MAP = self.zh2en_DOMAIN_MAP
        self.en2zh_INTENT_MAP = self.en2zh_DOMAIN_MAP

        # TODO: update below
        self.required_slots = {
            **{k: [] for k, v in self.DOMAIN_SLOT_MAP.items()},
            **{self.zh2en_DOMAIN_MAP.get(k, k): [] for k, v in self.DOMAIN_SLOT_MAP.items()},
        }
        self.api_names = list(self.required_slots.keys())

        self.zh2en_ACT_MAP = {
            # untranslated in the original dataset
            'inform': 'inform',
            'general': 'general',
            'greeting': 'greeting',
            'bye': 'bye',
            'request': 'request',
            'recommend': 'recommend',
            'no-offer': 'no-offer',
        }
        self.en2zh_ACT_MAP = {v: k for k, v in self.zh2en_ACT_MAP.items()}

        self.zh2en_SLOT_MAPS = {
            '区域': 'area',
            '名称': 'name',
            '门诊时间': 'service_time',
            '挂号时间': 'registration_time',
            'DSA': 'DSA',
            '3.0T MRI': '3.0T_MRI',
            '重点科室': 'key_departments',
            '电话': 'phone',
            '公交线路': 'bus_routes',
            '地铁可达': 'metro_station',
            'CT': 'CT',
            '等级': 'level',
            '性质': 'public_or_private',
            '类别': 'general_or_specialized',
            '地址': 'address',
            '温度': 'temperature',
            '目的地': 'destination',
            '日期': 'date',
            '城市': 'city',
            '风力风向': 'wind',
            '天气': 'weather_condition',
            '紫外线强度': 'UV_intensity',
            '门票价格': 'ticket_price',
            '电话号码': 'phone_number',
            '菜系': 'cuisine',
            '评分': 'score',
            '最适合人群': 'the_most_suitable_people',
            '房费': 'room_charge',
            '景点类型': 'type',
            '房型': 'room_type',
            '推荐菜': 'dishes',
            '消费': 'consumption',
            '开放时间': 'opening_hours',
            '价位': 'pricerange',
            '是否地铁直达': 'metro_station',
            '特点': 'features',
            '座椅通风': 'ventilated_seats',
            '油耗水平': 'fuel_consumption',
            '级别': 'size',
            '能源类型': 'hybrid',
            '价格': 'price',
            '驱动方式': '4WD',
            '所属价格区间': 'pricerange',
            '车型': 'classification',
            '座位数': 'number_of_seats',
            '座椅加热': 'heated_seats',
            '倒车影像': 'parking_assist_system',
            '定速巡航': 'cruise_control_system',
            '动力水平': 'power_level',
            '车系': 'series',
            '厂商': 'brand',
            '出发时间': 'departure_time',
            '票价': 'ticket_price',
            '舱位档次': 'class_cabin',
            '时长': 'duration',
            '到达时间': 'arrival_time',
            '车次信息': 'train_number',
            '出发地': 'departure',
            '准点率': 'punctuality_rate',
            '航班信息': 'flight_information',
            '坐席': 'seat_type',
            '制片国家/地区': 'production_country_or_area',
            '豆瓣评分': 'Douban_score',
            '片名': 'title',
            '主演名单': 'name_list',
            '具体上映时间': 'release_date',
            '导演': 'director',
            '片长': 'film_length',
            '类型': 'type',
            '年代': 'decade',
            '主演': 'star',
            '价格区间': 'pricerange',
            '内存容量': 'memory_capacity',
            '商品名称': 'product_name',
            '显卡型号': 'GPU_model',
            '裸机重量': 'weight',
            '品牌': 'brand',
            '系统': 'operating_system',
            'CPU型号': 'CPU_model',
            '系列': 'series',
            '特性': 'features',
            '屏幕尺寸': 'screen_size',
            '游戏性能': 'game_performance',
            '分类': 'usage',
            '产品类别': 'computer_type',
            '待机时长': 'standby_time',
            '色系': 'colour',
            '硬盘容量': 'hard_disk_capacity',
            'CPU': 'CPU',
            '显卡类别': 'GPU_category',
            '首播时间': 'premiere_time',
            '集数': 'episodes',
            '单集片长': 'episode_length',
            '开始日期': 'start_date',
            '老师': 'teacher',
            '教师': 'teacher',
            '上课方式': 'type',
            '校区': 'campus',
            '难度': 'level',
            '时段': 'time',
            '课时': 'hours',
            '科目': 'subject',
            '班号': 'class_number',
            '结束日期': 'end_date',
            '年级': 'grade',
            '下课时间': 'end_time',
            '教室地点': 'classroom',
            '每周': 'day',
            '课次': 'times',
            '上课时间': 'start_time',
            '星级': 'star',
            '地铁是否直达': 'metro_station',
            '停车场': 'parking',
            '酒店类型': 'hotel_type',
            '起飞时间': 'departure_time',
            '营业时间': 'business_hours',
            '人均消费': 'per_capita_consumption',
            # below are google translated
            "车身尺寸(mm)": "body_size(mm)",
            "发动机排量(L)": "engine_displacement(L)",
            "发动机马力(Ps)": "engine_horsepower(Ps)",
            "综合油耗(L/100km)": "comprehensive_fuel_consumption(L/100km)",
            "环保标准": "environmental_standards",
            "驾驶辅助影像": "driving_assistance_video",
            "巡航系统": "cruise_system",
            "价格(万元)": "price",
            "地铁线路": "subway_line",
            "课程网址": "course_URL",
            "教师网址": "teacher_URL",
        }
        self.zh2en_SLOT_MAP = self.zh2en_SLOT_MAPS
        self.en2zh_SLOT_MAP = {v: k for k, v in self.zh2en_SLOT_MAP.items()}

        translation_dict = {
            **self.zh2en_DOMAIN_MAP,
            **self.zh2en_SLOT_MAP,
            **self.zh2en_ACT_MAP,
            **self.zh2en_RELATION_MAP,
            **self.zh2en_SPECIAL_MAP,
        }
        self.translation_dict = OrderedDict(sorted(translation_dict.items(), key=lambda item: len(item[0]), reverse=True))

        self.skip_slots_for_kb = {
            '_id',
            'fuel_consumption',
            'body_size(mm)',
            'engine_displacement(L)',
            'engine_horsepower(Ps)',
            'comprehensive_fuel_consumption(L/100km)',
            'environmental_standards',
            'driving_assistance_video',
            'cruise_system',
            'subway_line',
            'course_URL',
            'teacher_URL',
        }
        self.skip_slots_for_kb.update([self.en2zh_SLOT_MAP.get(slot) for slot in self.skip_slots_for_kb])
