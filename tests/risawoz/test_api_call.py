from collections import defaultdict

import dictdiffer

from dialogues import Risawoz
from dialogues.bitod.src.utils import span2knowledge


def api_result_diff(knowledge, gold_knowledge):
    knowledge = span2knowledge(knowledge)
    processed_knowledge = defaultdict(dict)
    for d in gold_knowledge.keys():
        gold_knowledge[d] = {s: str(v) for s, v in gold_knowledge[d].items()}
    for d in knowledge.keys():
        for sv in knowledge[d]:
            processed_knowledge[d][sv['slot']] = str(sv['value'][0])
    return list(dictdiffer.diff(dict(processed_knowledge), gold_knowledge))


if __name__ == "__main__":

    api_list = ["酒店", "旅游景点"]
    dialogue_state = {
        "酒店": {'价位': {'relation': '等于', 'value': ['偏贵']}, '区域': {'relation': '等于', 'value': ['吴江']}},
        "旅游景点": {"名称": {'relation': '等于', 'value': ['金鸡湖景区']}},
    }
    src_lang = 'zh'
    knowledge = defaultdict(dict)

    # mongodb_host = "mongodb://localhost:27017/"

    dataset = Risawoz()
    new_knowledge_text, constraints = dataset.make_api_call(dialogue_state, knowledge, api_list, src_lang='zh_CN')
    gold_knowledge = {
        '酒店': {
            '名称': '苏州黎里水岸寒舍精品酒店',
            '区域': '吴江',
            '星级': '5',
            '价位': '偏贵',
            '酒店类型': '商务出行',
            '房型': '大床房',
            '停车场': '免费',
            '房费': '629元',
            '地址': '苏州吴江区黎里镇南新街5-9号',
            '电话号码': '180-5181-5602',
            '评分': 4.6,
            '可用选项': 4,
        },
        '旅游景点': {
            '名称': '金鸡湖景区',
            '区域': '工业园区',
            '景点类型': '山水景区',
            '最适合人群': '情侣约会',
            '消费': '偏贵',
            '是否地铁直达': '是',
            '门票价格': '免费',
            '电话号码': '400-7558558',
            '地址': '苏州市工业园区星港街158号',
            '评分': 4.5,
            '开放时间': '全天',
            '特点': '看东方之门等高楼，坐摩天轮，乘船夜游，感受苏州现代化的一面。',
            '可用选项': 1,
        },
    }

    print('diff:', api_result_diff(new_knowledge_text, gold_knowledge))
