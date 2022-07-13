import argparse
import os
import sys

import ujson

from dialogues.risawoz.main import Risawoz

risawoz = Risawoz()


def get_input_output(dic):
    dial_ids = []
    turn_ids = []
    inputs = []
    outputs = []
    for turn in dic["data"]:
        if turn['train_target'] not in ["dst", "da"]:
            continue

        dial_id = turn['dial_id']
        turn_id = turn['turn_id']
        input = turn['input_text']
        output = turn['output_text']
        state = risawoz.span2state(output)
        dial_ids.append(dial_id)
        turn_ids.append(turn_id)
        inputs.append(input)
        outputs.append(state)

    return dial_ids, turn_ids, inputs, outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory",
        type=str,
        default='/Users/shiningsunnyday/Documents/GitHub/dialogues/dialogues/risawoz/data/Archive/',
        help='directory of files to check',
    )
    parser.add_argument("--setting", type=str, default='zh')
    parser.add_argument("--splits", type=str, nargs='+', default=['train', 'valid', 'test'])
    parser.add_argument("--version", type=int, default=5)
    args = parser.parse_args()
    for split in args.splits:
        with open(os.path.join(args.directory, f"{split}_entity_check.txt"), 'w+') as f:
            sys.stdout = f
            for (dial_id, turn_id, input, output) in zip(
                *get_input_output(
                    ujson.load(open(os.path.join(args.directory, f'{args.setting}_{split}_v{args.version}.json')))
                )
            ):
                for domain in output:
                    for (slot, value) in output[domain].items():
                        for v in value['value']:
                            if str(v) not in input:
                                print(f"dial_id: {dial_id}\nturn_id: {turn_id}\n\" {v} \" not in {input}\n")
