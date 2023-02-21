import argparse
import os
from pprint import pprint

import ujson

from dialogues import Bitod, Risawoz

parser = argparse.ArgumentParser()
parser.add_argument("--reference_file_path", type=str, default="data/test.json", help="path of reference")
parser.add_argument("--prediction_file_path", type=str, help="path of prediction")
parser.add_argument("--experiment", type=str, help="experiment name")
parser.add_argument("--setting", type=str, help="en, zh, en&zh, en2zh, zh2en")
parser.add_argument("--result_path", type=str, default="./", help="eval_model or eval_file?")
parser.add_argument("--save_prefix", type=str, default="", help="prefix of save file name")

args = parser.parse_args()

if 'bitod' in args.experiment:
    dataset = Bitod()
elif 'risawoz' in args.experiment:
    dataset = Risawoz(tgt=args.setting)

dataset.FAST_EVAL = False
dataset.DEBUG = True

if not args.setting:
    file = os.path.basename(args.reference_file_path)
    if 'zh' in file:
        args.setting = 'zh'
    else:
        args.setting = 'en'

if not os.path.exists(args.result_path):
    os.makedirs(args.result_path)

with open(args.reference_file_path) as f:
    reference_data = ujson.load(f)

with open(args.prediction_file_path) as f:
    predictions = ujson.load(f)

results = dataset.compute_result(predictions, reference_data)

pred_dir = os.path.dirname(args.prediction_file_path)
with open(os.path.join(pred_dir, "e2e_dialogue_results.json"), "w") as f:
    ujson.dump(
        {
            "JGA": results['jga'],
            "TSR": results['task_info'].get('Averaged_task_success', 0.0),
            "DSR": results['success_rate'],
            "API_Acc": results['api_acc'],
            "DA_Acc": results['da_acc'],
            "BLEU": results['bleu'],
            "SER": results['ser'],
        },
        f,
        indent=2,
        ensure_ascii=False,
    )

pprint(results)
print(
    results['jga'],
    results['task_info'].get('Averaged_task_success', 0.0),
    results['success_rate'],
    results['api_acc'],
    results['da_acc'],
    results['bleu'],
    results['ser'],
)
