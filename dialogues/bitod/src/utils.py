import json
import os
import re
import subprocess
from collections import defaultdict

from word2number import w2n

from dialogues.bitod.src.knowledgebase.en_zh_mappings import BitodMapping

value_mapping = BitodMapping()


def convert_to_int(val, strict=False, word2number=False):
    val = str(val)
    if val.isdigit() and not val.startswith('0'):
        return int(val)
    elif word2number and len(val.split()) == 1:
        # elif word2number:
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


def clean_text(text, is_formal=False):
    text = text.strip()
    text = re.sub(' +', ' ', text)
    text = re.sub('\\n|\\t', ' ', text)
    text = text.replace('，', ',')

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


def read_ontology(tgt_lang):
    all_ontologies = defaultdict(lambda: defaultdict(set))
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for fn in os.listdir(os.path.join(cur_dir, "knowledgebase/apis")):
        api_name = fn.replace(".json", "")
        _, rest = api_name.split('_', 1)
        lang = rest[:2]
        if lang != tgt_lang[:2]:
            continue

        api_name = value_mapping.API_MAP[api_name]

        with open(os.path.join(cur_dir, "knowledgebase/apis", fn)) as f:
            ontology = json.load(f)
            processed_ont = defaultdict(set)
            for key in ['input', 'output']:
                for item in ontology[key]:
                    slot, type = item['Name'], item['Type']
                    if lang == 'zh':
                        slot = value_mapping.en2zh_SLOT_MAP[slot]
                    if type == 'Categorical':
                        values = item['Categories']
                        values += [value_mapping.entity_map.get(val, val) for val in values]
                        values += [value_mapping.reverse_entity_map.get(val, val) for val in values]
                        values = set(values)
                        processed_ont[slot].update(values)
                    elif type == 'Integer':
                        values = list(range(item['Min'], item['Max'] + 1))
                        values += [value_mapping.entity_map.get(val, val) for val in values]
                        values += [value_mapping.reverse_entity_map.get(val, val) for val in values]
                        values = set(values)
                        processed_ont[slot].update(values)
                    else:
                        raise ValueError('bad type')

            all_ontologies[api_name] = processed_ont

    return all_ontologies
