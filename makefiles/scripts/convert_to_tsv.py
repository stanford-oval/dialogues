import argparse

import ujson

parser = argparse.ArgumentParser('BiTOD parser')

parser.add_argument('--input_file')
parser.add_argument('--output_file')

args = parser.parse_args()

data = ujson.load(open(args.input_file))['data']

with open(args.output_file, 'w') as fout:
    for item_dict in data:
        dial_id, task, turn_id, input_text, output_text, train_target = (
            item_dict['dial_id'],
            item_dict['task'],
            item_dict['turn_id'],
            item_dict['input_text'],
            item_dict['output_text'],
            item_dict['train_target'],
        )

        parts = [dial_id + '/' + str(turn_id) + '/' + train_target, input_text, output_text]
        line = '\t'.join(parts)
        fout.write(line + '\n')
