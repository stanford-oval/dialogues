import argparse

import ujson

parser = argparse.ArgumentParser('Dataset parser')

parser.add_argument('--input_file')
parser.add_argument('--output_file')

args = parser.parse_args()

data = []

with open(args.input_file) as fin:
    for line in fin:
        id_, sent, target = line.strip('\n').split('\t')
        
        if id_.startswith('bitod') or id_.startswith('risawoz'):
            task_name, dial_id, turn_id, train_target = id_.split('/')
        else:
            dial_id, turn_id, train_target = id_.split('/')
        
        data.append({
                   "dial_id": dial_id,
                   "task": "",
                   "turn_id": int(turn_id),
                   "input_text": sent,
                   "output_text": target,
                   "train_target": train_target
                  })
        
ujson.dump({"data": data}, open(args.output_file, 'w'), indent=True, ensure_ascii=False)

        
