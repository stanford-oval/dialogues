import argparse
import os

import ujson

from dialogues import Risawoz

risawoz = Risawoz()


def get_input_output(dic):
    dial_ids = []
    turn_ids = []
    inputs = []
    outputs = []
    entities = []
    for turn in dic["data"]:
        if turn['train_target'] not in ["dst", "da"]:
            continue

        dial_id = turn['dial_id']
        turn_id = turn['turn_id']
        input = turn['input_text']
        output = turn['output_text']

        dial_ids.append(dial_id)
        turn_ids.append(turn_id)
        inputs.append(input)
        outputs.append(output)

        ents = []

        if turn['train_target'] == 'dst':
            output = risawoz.span2state(output)
            for domain in output:
                for (slot, value) in output[domain].items():
                    for v in value['value']:
                        ents.append(str(v))
        else:
            output = risawoz.span2action(output)
            for domain in output:
                for item in output[domain]:
                    for v in item['value']:
                        ents.append(str(v))

        entities.append(ents)

    return dial_ids, turn_ids, inputs, outputs, entities


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, help='directory of files to check')
    parser.add_argument("--setting", type=str, default='zh')
    parser.add_argument("--splits", type=str, nargs='+', default=['train', 'valid', 'test'])
    parser.add_argument("--version", type=int, default=5)
    args = parser.parse_args()

    for split in args.splits:
        with open(os.path.join(args.directory, f"{split}_entity_check.tsv"), 'w+') as f:
            for (dial_id, turn_id, input, output, ents) in zip(
                *get_input_output(
                    ujson.load(open(os.path.join(args.directory, f'{args.setting}_{split}_v{args.version}.json')))
                )
            ):
                for ent in ents:
                    if not ent:
                        continue
                    if ent not in input:
                        f.write(f"{dial_id}\t{turn_id}\t{input}\t{output}\t{ent}\n")
