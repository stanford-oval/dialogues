import argparse
import json
import os
from collections import OrderedDict

from dialogues import Risawoz

parser = argparse.ArgumentParser()

parser.add_argument('--input_db_dir', default='dialogues/risawoz/database/db_en')
parser.add_argument('--output_db_dir', default='dialogues/risawoz/database/db_en_new')
parser.add_argument('--experiment')

args = parser.parse_args()


dataset = Risawoz()
value_mapping = dataset.value_mapping

seen = set()
out = open('./out_ent.tsv', 'w')

os.makedirs(args.output_db_dir, exist_ok=True)

for file in os.listdir(args.input_db_dir):
    domain = file.split('_', 1)[0]
    if domain.startswith('.'):
        continue
    # if domain not in value_mapping.en2zh_DOMAIN_MAP.keys():
    #     continue
    db_info = json.load(open(os.path.join(args.input_db_dir, file)))

    translated_db_info = []

    for item in db_info:
        translated_item = OrderedDict()
        for slot, value in item.items():
            # if slot not in value_mapping.zh2en_SLOT_MAP:
            #     if slot not in seen:
            #         print(slot)
            #         seen.add(slot)
            #     continue
            #
            # def find_new(value):
            #     value = str(value)
            #     for in_pattern, out_pattern in all_replacements.items():
            #         if re.fullmatch(in_pattern, value):
            #             new_value = re.sub(in_pattern, out_pattern, value)
            #             return new_value
            #
            #     return None

            # is_list = True
            # if not isinstance(value, list):
            #     is_list = False
            #     value = [value]
            # new_value = []
            # for val in value:
            #
            #     if val in [True, False]:
            #         new_value.append(val)
            #     elif val in value_mapping.zh2en_VALUE_MAP:
            #         new_value.append(value_mapping.zh2en_VALUE_MAP[val])
            #     elif val in value_mapping.zh2en_missing_MAP:
            #         new_value.append(value_mapping.zh2en_missing_MAP[val])
            #     elif find_new(val):
            #         new_value.append(find_new(val))
            #     else:
            #         if (
            #             val not in seen
            #             and not str(val).startswith('http:')
            #             and not re.fullmatch('[A-Z0-9]+', str(val))
            #             and not re.fullmatch('[\d\.:\-]+', str(val))
            #             and val not in [True, False]
            #         ):
            #             print(val)
            #             out.write(str(val) + '\n')
            #             seen.add(val)
            #
            #         if isinstance(val, str) and val.endswith('。') and slot == '特点':
            #             val = val[:-1]
            #
            #         new_value.append(val)
            #
            # value = new_value
            #
            # if not is_list:
            #     if not len(value):
            #         continue
            #     assert len(value) == 1
            #     value = value[0]

            # if isinstance(value, str) and value.endswith('。') and slot == '特点':
            #     value = value[:-1]
            #
            # value = process_string(value)
            #
            # translated_item[value_mapping.zh2en_SLOT_MAP[slot]] = value

            translated_item[slot.replace(' ', '_')] = value

        translated_db_info.append(translated_item)

    json.dump(
        translated_db_info, open(os.path.join(args.output_db_dir, domain + '_en.json'), 'w'), ensure_ascii=False, indent=2
    )
