import argparse
import re
import sys

sys.path.append('../')
from dialogues import WOZDataset

parser = argparse.ArgumentParser('BiTOD parser')

parser.add_argument('--translated_file_user')
parser.add_argument('--translated_file_agent')
parser.add_argument('--ref_file')
parser.add_argument('--output_file')

args = parser.parse_args()

dataset = WOZDataset()

translated_user = []
with open(args.translated_file_user) as fin:
    for line in fin:
        sent = line.strip('\n').split('\t')[1]
        translated_user.append(sent)
translated_agent = []
with open(args.translated_file_agent) as fin:
    for line in fin:
        sent = line.strip('\n').split('\t')[1]
        translated_agent.append(sent)

def replace_match(input, re_pattern, replacement):
    whole_match = re_pattern.search(input).group(0).strip()
    match = re_pattern.search(input).group(1).strip()
    new_whole_match = whole_match.replace(match, replacement)
    return re.sub(re_pattern, new_whole_match, input)


with open(args.ref_file) as fin, open(args.output_file, 'w') as fout:
    trans_idx = 0
    for i, line in enumerate(fin):
        # proceed to the next turn
        if i % 4 == 0 and i != 0:
            trans_idx += 1
        id_, input, output = line.strip('\n').split('\t')
        
        # replace user utterance in history
        new_input = replace_match(input, dataset.user_re, translated_user[trans_idx])
        new_output = output
        
        # replace agent response for RG
        if i % 4 == 3 and i != 0:
            new_output = translated_agent[trans_idx]
        
        fout.write('\t'.join([id_, new_input, new_output]) + '\n')
        
        