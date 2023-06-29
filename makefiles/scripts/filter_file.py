import argparse
import re

from dialogues import Bitod, Risawoz

QUOTED_MATCH_REGEX = re.compile(' " (.*?) " ')

parser = argparse.ArgumentParser('')

parser.add_argument('--input_file')
parser.add_argument('--output_file')
parser.add_argument('--task_name')

args = parser.parse_args()

if args.task_name == 'bitod':
    dataset = Bitod()
elif args.task_name == 'risawoz':
    dataset = Risawoz()

dst, api, da, rg = 0, 0, 0, 0
total = 0

with open(args.input_file) as fin, open(args.output_file, 'w') as fout:
    for line in fin:
        id_, pred, gold, input = line.strip('\n').split('\t')
        total += 1

        if id_.endswith('/dst'):
            if dataset.compute_dst_em([dataset.span2state(pred)], [dataset.span2state(gold)]) == 100:
                fout.write(line)
                dst += 1

        elif id_.endswith('/api'):
            if pred == gold:
                fout.write(line)
                api += 1

        elif id_.endswith('/da'):
            if dataset.compute_da([pred], [gold]) == 100:
                fout.write(line)
                da += 1

        elif id_.endswith('/rg'):
            act_values = []
            act_values.append(QUOTED_MATCH_REGEX.findall(input))
            if dataset.compute_ser(pred, act_values) == 0:
                fout.write(line)
                rg += 1

print(f'Kept {dst} examples for DST from {total // 4} examples')
print(f'Kept {api} examples for API from {total // 4} examples')
print(f'Kept {da} examples for DA from {total // 4} examples')
print(f'Kept {rg} examples for RG from {total // 4} examples')
