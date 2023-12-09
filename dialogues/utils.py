import json
import os
import re
import subprocess
from contextlib import ExitStack
from pathlib import Path

from word2number import w2n

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


def convert_to_int(val, strict=False, word2number=False):
    val = str(val)
    if val.isdigit() and not val.startswith('0'):
        return int(val)
    elif word2number and len(val.split()) == 1:
        try:
            num = w2n.word_to_num(val)
            return num
        except:
            if strict:
                return None
            else:
                return val
    else:
        if strict:
            return None
        else:
            return val


# very slow
def replace_word(input, search, replace):
    def replace_method(match):
        if match.group(2) is None:
            return match.group()
        return match.group(2).replace(search, replace)

    expr = re.compile(f"(\"[^\"]*\")|( {search}(?:$| ))")
    return re.sub(expr, replace_method, input)


def clean_text(text, is_formal=False):
    text = text.strip()
    text = re.sub(' +', ' ', text)
    text = re.sub('\\n|\\t', ' ', text)
    text = text.replace('，', ',')
    text = text.replace('，', ',')
    text = text.replace('？', '?')
    text = text.replace('！', '!')

    if not is_formal:
        text = text.replace('"', '')

    return text


def get_commit():
    directory = os.path.dirname(__file__)
    return (
        subprocess.Popen("cd {} && git log | head -n 1".format(directory), shell=True, stdout=subprocess.PIPE)
        .stdout.read()
        .split()[1]
        .decode()
    )


is_mongo = True


def is_equal_to(value):
    if is_mongo:
        return value
    else:
        return lambda x: x == value


def is_not(value):
    if is_mongo:
        return {"$ne": value}
    else:
        return lambda x: x != value


def contains_none_of(value):
    if is_mongo:
        return {"$nin": value}
    else:
        return lambda x: not any([e in x for e in value])


def is_one_of(value):
    if is_mongo:
        return {"$in": value}
    else:
        return lambda x: x in value


def is_at_least(value):
    if is_mongo:
        return {"$gte": value}
    else:
        return lambda x: x >= value


def is_less_than(value):
    if is_mongo:
        return {"$lt": value}
    else:
        return lambda x: x < value


def is_at_most(value):
    if is_mongo:
        return {"$lte": value}
    else:
        return lambda x: x <= value


def contain_all_of(value):
    return lambda x: all([e in x for e in value])


def contain_at_least_one_of(value):
    return lambda x: any([e in x for e in value])


def constraint_and(constraint1, constraint2):
    return lambda x: constraint1(x) and constraint2(x)


def constraint_list_to_dict(constraints):
    result = {}
    for constraint in constraints:
        for name, constraint_function in constraint.items():
            if name not in result:
                result[name] = constraint_function
            else:
                result[name] = constraint_and(result[name], constraint_function)
    return result


def read_json_files_in_folder(path):
    json_filename = [path + '/' + filename for filename in os.listdir(path) if '.json' in filename]
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in json_filename]
        data = {}
        for i in range(len(files)):
            data[Path(json_filename[i]).stem] = json.load(files[i])
    return data

def read_jsonl_files_in_folder(path):
    json_filename = [path + '/' + filename for filename in os.listdir(path) if '.jsonl' in filename]
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in json_filename]
        data = {}
        for i in range(len(files)):
            json_list = list(files[i])
            result = []
            for json_str in json_list:
                result.append(json.loads(json_str))
            data[Path(json_filename[i]).stem] = result
    return data
