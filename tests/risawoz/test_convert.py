import argparse
import json
import os
import subprocess

from dialogues import Risawoz
from dialogues.risawoz.src.convert import build_dataset, build_db

parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, default='dialogues/risawoz/', help='code root directory')
parser.add_argument("--data_dir", type=str, default="data/original/", help="path to original data, relative to root dir")
parser.add_argument("--save_dir", type=str, default="data/", help="path to save preprocessed data, relative to root dir")
parser.add_argument("--setting", type=str, help="en, zh, en_zh")
parser.add_argument("--splits", nargs='+', default=['valid'])

args = parser.parse_args()

mongodb_host = "mongodb://localhost:27017/"

if args.setting in ['en', 'zh', 'hi']:
    src, tgt = 'zh', 'en'
else:
    src, tgt = 'en', args.setting


dataset = Risawoz(src=src, tgt=tgt, mongodb_host=mongodb_host)


risawoz_db = build_db(
    db_json_path=os.path.join(*[args.root, f'database/db_{args.setting}']),
    api_map=None,
    setting=args.setting,
    value_mapping=dataset.value_mapping,
    mongodb_host=mongodb_host,
)


original_data_path = os.path.join(*[args.root, args.data_dir])

for split in args.splits:
    print(f"processing {split} data...")
    processed_data = build_dataset(
        os.path.join(original_data_path, f"{args.setting}_{split}.json"),
        risawoz_db,
        args.setting,
        dataset.value_mapping,
        debug=False,
    )

    with open(f'{args.setting}_converted_valid.json', 'w') as fout:
        json.dump(processed_data, fout, indent=4, ensure_ascii=False)

    with open(f'./tests/risawoz/data/{args.setting}/converted_valid.json') as f:
        gold_data = json.load(f)

    print(
        subprocess.Popen(
            f"diff -u {args.setting}_converted_valid.json ./tests/risawoz/data/{args.setting}/converted_valid.json",
            shell=True,
            stdout=subprocess.PIPE,
        )
        .stdout.read()
        .decode()
    )
    assert processed_data == gold_data
