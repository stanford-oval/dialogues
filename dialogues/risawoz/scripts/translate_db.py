import argparse
import json
import os
import re

from dialogues import Risawoz

parser = argparse.ArgumentParser()

parser.add_argument('--input_db_dir', default='dialogues/risawoz/db')
parser.add_argument('--output_db_dir', default='dialogues/risawoz/db_en')
parser.add_argument('--experiment')

args = parser.parse_args()


dataset = Risawoz()
value_mapping = dataset.value_mapping

seen = set()
out = open('./out_ent.tsv', 'w')

all_replacements = {}

all_replacements.update({'否': r'no'})

all_replacements.update({'当天 (\d{2}:\d{2})': r'\1 today'})

all_replacements.update({'(\d+\.?\d?)元': r'\1 yuan'})

all_replacements.update({'(\d{4}-\d{2}-\d{2})\(韩国\)': r'\1(South Korea)'})
all_replacements.update({'(\d{4}-\d{2}-\d{2})\(中国香港\)': r'\1(Hong Kong, China)'})
all_replacements.update({'(\d{4}-\d{2}-\d{2})\(日本\)': r'\1(Japan)'})
all_replacements.update({'(\d{4}-\d{2}-\d{2})\(美国\)': r'\1(USA)'})
all_replacements.update({'(\d{4}-\d{2}-\d{2})\(中国台湾\)': r'Taiwan, China'})
all_replacements.update({'(\d{4}-\d{2}-\d{2})\(中国大陆\)': r'Mainland, China'})

all_replacements.update({'周一至周日 (\d{2}:\d{2}-\d{2}:\d{2})': r'Monday to Sunday \1'})
all_replacements.update({'周一至周日 (\d{2}:\d{2}-\d{2}:\d{2}) (\d{2}:\d{2}-\d{2}:\d{2})': r'Monday to Sunday \1 \2'})


all_replacements.update({'(\d{4}/\d{1,2}/\d{1,2})': r'\1'})


for file in os.listdir(args.input_db_dir):
    domain = file.split('_', 1)[0]
    if domain.startswith('.'):
        continue
    # if domain not in value_mapping.en2zh_DOMAIN_MAP.keys():
    #     continue
    db_info = json.load(open(os.path.join(args.input_db_dir, file)))

    translated_db_info = []

    for item in db_info:
        translated_item = {}
        for slot, value in item.items():
            if slot not in value_mapping.zh2en_SLOT_MAP:
                if slot not in seen:
                    print(slot)
                    seen.add(slot)
                continue

            def find_new(value):
                value = str(value)
                for in_pattern, out_pattern in all_replacements.items():
                    if re.fullmatch(in_pattern, value):
                        new_value = re.sub(in_pattern, out_pattern, value)
                        return new_value

                return None

            is_list = True
            if not isinstance(value, list):
                is_list = False
                value = [value]
            new_value = []
            for val in value:
                if val in [True, False]:
                    new_value.append(val)
                elif val in value_mapping.zh2en_VALUE_MAP:
                    new_value.append(value_mapping.zh2en_VALUE_MAP[val])
                elif val in value_mapping.zh2en_missing_MAP:
                    new_value.append(value_mapping.zh2en_missing_MAP[val])
                elif find_new(val):
                    new_value.append(find_new(val))
                else:
                    if (
                        val not in seen
                        and not str(val).startswith('http:')
                        and not re.fullmatch('[A-Z0-9]+', str(val))
                        and not re.fullmatch('[\d\.:\-]+', str(val))
                        and val not in [True, False]
                    ):
                        print(val)
                        out.write(str(val) + '\n')
                        seen.add(val)
                    new_value.append(val)

            value = new_value

            if not is_list:
                if not len(value):
                    continue
                assert len(value) == 1
                value = value[0]

            translated_item[value_mapping.zh2en_SLOT_MAP[slot]] = value

        translated_db_info.append(translated_item)

    json.dump(
        translated_db_info, open(os.path.join(args.output_db_dir, domain + '_en_US.json'), 'w'), ensure_ascii=False, indent=2
    )
