import argparse
import json
from collections import defaultdict

from dialogues.risawoz.src.knowledgebase.api import process_string

parser = argparse.ArgumentParser()

parser.add_argument('--input_file', default='dialogues/risawoz/src/knowledgebase/mappings/zh2en_alignment.json')

args = parser.parse_args()


zh2en_value = defaultdict(lambda: defaultdict(dict))

with open(args.input_file) as fin:
    zh2en_alignment = json.load(fin)
    for domain, items in zh2en_alignment.items():
        for slot, values in items.items():
            for zh_val, en_vals in values.items():
                zh_val = zh_val.replace('，', ',')
                zh_val = zh_val.replace('：', ':')
                value = process_string(zh_val, setting='zh')
                zh2en_value[domain][slot][value] = en_vals

with open(args.input_file.replace('zh2en_alignment.json', 'zh2en_alignment_new.json'), 'w') as fout:
    json.dump(zh2en_value, fout, ensure_ascii=False, indent=4)
