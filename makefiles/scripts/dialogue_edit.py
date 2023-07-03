import argparse
import collections
import json
import os.path
import random
import re

import sys

from dialogues.utils import ENGLISH_MONTH_MAPPING, zh2en_DAY_MAP, en2zh_DAY_MAP, MONTH_MAPPING_EN, MONTH_MAPPING_ZH
from dialogues.bitod.src.knowledgebase.hk_mtr import name_to_zh, rev_name_to_zh
from dialogues.risawoz.src.knowledgebase.api import process_string
from tqdm import tqdm

from dialogues import Bitod, Risawoz

sys.path.append('../')

DELIM = "\t"
DONTCARE = "don't care"
NULL = 'null'

global_count = 0
dataset = None

def fresh_placeholder(value=None):
    global global_count
    if value:
        retval = '@' + str(value)
    else:
        retval = '@' + str(global_count)
        global_count += 1
    return retval


class TrieNode(object):
    def __init__(self):
        self.key = ''
        self.children = {}
    
    def insert(self, word, key, index=0):
        if index >= len(word):
            if self.key == '':
                self.key = sample_value(word)
            return self.key
        if word[index] not in self.children:
            self.children[word[index]] = TrieNode()
        return self.children[word[index]].insert(word, key, index + 1)
    
    def print(self, s=''):
        print('%s  key %s' % (s, self.key))
        for k in self.children:
            print('%s%s:' % (s, k))
            self.children[k].print(s + ' ')


# Assumes correct formatting
def process_line(line):
    arr = line.split(DELIM)
    ids = arr[0].split('/')
    assert len(ids) == 3, "Wrong id format: Should be ID/TURN."

    input = arr[1].strip('\n')
    output = arr[2].strip('\n')
    
    return ids[0], ids[1], ids[2], input, output

def update_entities(trie_root, text, train_target, side):
    new_text_dict = {}
    
    if side == 'output':
        if train_target == 'dst':
            text_dict = dataset.span2state(text)
            new_text_dict = {}
            for intent, slot_dicts in text_dict.items():
                for slot, rvs in slot_dicts.items():
                    key = f"{intent} {slot} {rvs['relation']}"
                    new_text_dict[key] = ' | '.join(map(str, rvs['value']))
            
        elif train_target == 'da':
            text_dict = dataset.span2action(text)
            new_text_dict = {}
            for intent, asrvs in text_dict.items():
                for item in asrvs:
                    key = f"{intent} {item['slot']} {item['relation']}"
                    new_text_dict[key] = ' | '.join(map(str, item['value']))
                    
    else:
        # state = state_re.findall(text)
        knowledge = dataset.knowledge_re.findall(text)
        new_text_dict = {}
        if knowledge:
            text_dict = dataset.span2knowledge(knowledge[0])
            for intent, svs in text_dict.items():
                for item in svs:
                    key = f"{intent} {item['slot']}"
                    new_text_dict[key] = ' | '.join(map(str, item['value']))

    # sort by entity length
    new_text_dict = dict(sorted(new_text_dict.items(), key=lambda item: len(item[1]), reverse=True))
    
    for key, val in new_text_dict.items():
        values = val.split(' | ')
        for val in values:
            if val in [DONTCARE, NULL]:
                continue
            else:
                trie_root.insert(val, key)

    return text


def replace(utterance, entities):
    confirmed = []
    matches = collections.deque([])
    match = None
    # Find matches
    for i in range(len(utterance)):
        cur_len = len(matches)
        cur_char = utterance[i]
        for j in range(cur_len):
            match = matches.popleft()
            if match[1].key != '':
                # start index, replace string, end index
                confirmed.append((match[0], match[1].key, i))
            if cur_char in match[1].children:
                matches.append((match[0], match[1].children[cur_char]))
        if cur_char in entities.children:
            matches.append((i, entities.children[cur_char]))
    if len(matches):
        match = matches.popleft()
        if match[1].key != '':
            confirmed.append((match[0], match[1].key, i))
    
    # Check overlaps
    fully_confirmed = []
    for i in range(len(confirmed)):
        if utterance[confirmed[i][0]:confirmed[i][2]] == 'one' and utterance[confirmed[i][0]-2:confirmed[i][0]+10] == 'phone_number':
            continue
        if utterance[confirmed[i][0]:confirmed[i][2]] == '一' and utterance[confirmed[i][0]-3:confirmed[i][0]+1] == '其中之一':
            continue
        if utterance[confirmed[i][0]:confirmed[i][2]] in ['香港', '香港地'] and utterance[confirmed[i][0]:confirmed[i][0]+4] == '香港地铁':
            continue
        keep = True
        for j in range(len(confirmed)):
            if i == j:
                continue
            # pairwise overlap, choose longer of the two.
            if confirmed[i][0] >= confirmed[j][0] and confirmed[i][2] <= confirmed[j][2]:
                keep = False
        if keep:
            fully_confirmed.append(confirmed[i])
    
    # Replace
    if fully_confirmed == []:
        return utterance
    cursor = 0
    new_utterance = ''
    for (start_ind, replace, end_ind) in fully_confirmed:
        new_utterance += utterance[cursor:start_ind]
        if mode == 'qpis' and not new_utterance.endswith(('" ', '| ')):
            replace = ' ## ' + replace + ' ## '
        new_utterance += str(replace)
        new_utterance = new_utterance.replace('  ', ' ')
        cursor = end_ind
    if cursor < len(utterance) - 1:
        new_utterance += utterance[cursor:]
    new_utterance = new_utterance.replace('##', '"')


    return new_utterance


sets = set()
file = open('out.tsv', 'w')

def sample_value(value):
    # don't touch numbers (dates, currency value, confirmation #, etc.)
    value = value.strip('@')
    if re.match('^[0-9]+$', value) or value in ["don't care", "不在乎"] or re.match('\+?[0-9- ]+', value) or value.startswith('http://'):
        return value
    
    # qpis
    if mode == 'qpis':
        return value
    
    # Requote
    elif mode == 'requote':
        return fresh_placeholder(value)
    
    # Augment
    elif mode == 'augment':
        
        if args.aug_mode == 'dictionary':
            value = value.strip('@')
            possible_transformations = [value, process_string(value, setting=args.src_lang), value.lower(), value.replace('／', '/'), value.replace('/', '／')]

            if args.tgt_lang == 'en':
                MONTH_MAPPING = MONTH_MAPPING_EN
                rev_canonical_map = dataset.value_mapping.rev_en2canonical
                value_map = dataset.value_mapping.zh2en_VALUE_MAP
                day_map = zh2en_DAY_MAP
                mtr_map = rev_name_to_zh
                missing_map = dataset.value_mapping.zh2en_missing_MAP
            else:
                # fix below
                MONTH_MAPPING = MONTH_MAPPING_ZH
                day_map = en2zh_DAY_MAP
                mtr_map = name_to_zh
                rev_canonical_map = dataset.value_mapping.rev_en2canonical
                missing_map = eval(f'dataset.value_mapping.zh2{args.tgt_lang}_missing_MAP')
                value_map = dataset.value_mapping.zh2en_VALUE_MAP
                # missing_map = {}

            def find_val(val):
                trans_val = value_map[val]
                if trans_val in rev_canonical_map:
                    val_options = rev_canonical_map[trans_val]
                    if not isinstance(val_options, list):
                        val_options = [val_options]
                    index = random.randint(0, len(val_options) - 1)
                    return val_options[index]
                else:
                    return trans_val
            
            for val in possible_transformations:
                if val in value_map:
                    return find_val(val)

            all_replacements = {}
            if args.src_lang == 'en' and args.tgt_lang == 'zh':
                english_months = '|'.join(ENGLISH_MONTH_MAPPING.values())
    
                all_replacements.update({'([\d\.]+) HKD': r'\1港币', '([\d\.]+) mins': r'\1分钟'})
    
                all_replacements.update({f'((?:{english_months})) (\d+)': r'\1月\2日'})

                all_replacements.update({'([\d\:]+) (?:afternoon|in the afternoon)': r'下午\1', '([\d\:]+) (?:morning|in the morning)': r'上午\1'})

                all_replacements.update({'(\d+):(\d+) am': r'早上\1点\2分', '(\d+):(\d+) pm': r'(?:晚上|下午)\1点\2分'})

                all_replacements.update({r'You will depart from (.+?) and arrive at (.+?).': r'你将从\1出发,抵达\2。'})
            
            elif args.src_lang == 'zh' and args.tgt_lang == 'en':
                all_replacements.update({'([\d\.]+)港币': r'\1 HKD', '([\d\.]+)分钟': r'\1 mins'})
    
                all_replacements.update({'下午([\d\:]+)': r'\1 afternoon', '上午([\d\:]+)': r'\1 morning'})
    
                all_replacements.update({'(?:晚上|下午)(\d+)点(\d+)分': r'\1:\2 pm'})
                all_replacements.update({'早上(\d+)点(\d+)分': r'\1:\2 am'})
    
                all_replacements.update({'(\d+)月(\d+)日': r'\1 month \2'})
    
                all_replacements.update({'你将从(.+?)出发[,，]抵达(.+?)。': r'You will depart from \1 and arrive at \2.'})
            
            def find_new(value):
                for in_pattern, out_pattern in all_replacements.items():
                    if re.fullmatch(in_pattern, value):
                        new_value = re.sub(in_pattern, out_pattern, value)
                        for k, v in MONTH_MAPPING.items():
                            if k in new_value:
                                new_value = new_value.replace(k, v)
                                break
                        return new_value
            
                return None
             
            
            expanded_values = [value, value.strip('[]').strip("'"), value + '。', value.strip('。'), dataset.value_mapping.entity_map.get(value, None), dataset.value_mapping.reverse_entity_map.get(value, None)]
            for val in expanded_values:
                if not val:
                    continue
                val = str(val)
                if val.isdigit():
                    return val
                if val in value_map:
                    return find_val(val)
                if val in day_map:
                    return day_map[val]
                if val in mtr_map:
                    return mtr_map[val]
                new_val = find_new(val)
                if re.match('^[A-Z][0-9]+$', val):
                    return value
                if new_val:
                    return new_val
                
            if value in missing_map:
                return missing_map[value]
        
            # reservation confirmation number
            if re.fullmatch('[A-Z\d]+', value):
                return value
        
        if value not in sets:
            sets.add(value)
            if not value.startswith('Take the'):
                file.write(value + '\n')
                print(f'***error: could not translate {value}')

        return value

def format_line(line_id, turn, train_target, input, output):
    out_str = line_id + '/' + turn + '/' + train_target + DELIM + input + DELIM + output
    return out_str + "\n"


def main(args):
    print('Writing to file %s\n' % (args.output_path))
    
    curr_id = ''
    entities = TrieNode()

    num_lines = 0
    with open(args.input_path, 'r') as data:
        for _ in data:
            num_lines += 1
    
    with open(args.input_path, 'r') as data, open(args.output_path, 'w') as out:
        for line in tqdm(data, total=num_lines):
            line_id, turn, train_target, input, output = process_line(line)
            
            if train_target == '/rg':
                input, output = output, input

            if line_id != curr_id:
                curr_id = line_id
                entities = TrieNode()

            update_entities(entities, output, train_target, 'output')
            update_entities(entities, input, train_target, 'input')
            
            new_input = replace(input, entities)
            new_output = replace(output, entities)
            
            if train_target == '/rg':
                new_input, new_output = new_output, new_input
            
            if args.tgt_lang == 'en':
                new_input = new_input.replace('HKMTR zh', 'HKMTR en')
                new_output = new_output.replace('HKMTR zh', 'HKMTR en')
            else:
                new_input = new_input.replace('HKMTR en', 'HKMTR zh')
                new_output = new_output.replace('HKMTR en', 'HKMTR zh')
            
            out.write(format_line(line_id, turn, train_target, new_input, new_output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', default="./data_raw", type=str)
    parser.add_argument('--output_path', default="./data_repl", type=str)
    parser.add_argument('--ontology', type=str)
    parser.add_argument('--experiment', type=str)
    parser.add_argument('--mode', default='requote', choices=['requote', 'augment', 'qpis'], type=str)
    parser.add_argument('--seed', default=123, type=int)
    parser.add_argument('--src_lang', type=str)
    parser.add_argument('--tgt_lang', type=str)
    parser.add_argument('--sampling_method', type=str, default='random', choices=['random', 'first'])
    parser.add_argument('--nlg', action='store_true')
    parser.add_argument('--aug_mode', default='random', choices=['random', 'dictionary'])

    args = parser.parse_args()
    
    random.seed(args.seed)

    mode = args.mode
    
    if args.ontology and os.path.exists(args.ontology):
        ontology = json.load(open(args.ontology))
    
    if 'risawoz' in args.experiment:
        dataset = Risawoz(src=args.src_lang, tgt=args.tgt_lang)
        # dataset = Risawoz()
    elif 'bitod' in args.experiment:
        dataset = Bitod()

    main(args)
