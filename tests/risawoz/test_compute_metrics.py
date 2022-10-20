import argparse
import os
from collections import OrderedDict

import dictdiffer

from dialogues import Risawoz

parser = argparse.ArgumentParser()

parser.add_argument(
    "--reference_file_path", type=str, default="./tests/risawoz/data/converted_valid.json", help="path of reference"
)
parser.add_argument("--prediction_file_path", type=str, default="tests/risawoz/data/preds.json", help="path of prediction")
parser.add_argument("--eval_task", type=str, default="end2end", help="end2end, dst, response")
parser.add_argument("--setting", type=str, help="en, zh, en&zh, en2zh, zh2en")
parser.add_argument("--result_path", type=str, default="./", help="result_path")
parser.add_argument("--save_prefix", type=str, default="", help="prefix of save file name")

args = parser.parse_args()

if not os.path.exists(args.result_path):
    os.makedirs(args.result_path)

if not args.setting:
    file = os.path.basename(args.reference_file_path)
    if 'zh' in file:
        args.setting = 'zh'
    else:
        args.setting = 'en'

dataset = Risawoz()
dataset.FAST_EVAL = True
results = dataset.compute_metrics(args, args.prediction_file_path, args.reference_file_path)

# api, da, and ser are not correct
gold_results = OrderedDict(
    [
        ('bleu', 46.0014),
        ('ser', 18.260226712666338),
        ('success_rate', 58.5),
        ('api_acc', 83.27485380116958),
        ('da_acc', 73.90340068999507),
        ('jga', 82.97190734351898),
        (
            'task_info',
            {
                'attraction': {'total': 120, 'hit': 104, 'success_rate': 0.8666666666666667},
                'restaurant': {'total': 120, 'hit': 101, 'success_rate': 0.8416666666666667},
                'hotel': {'total': 120, 'hit': 60, 'success_rate': 0.5},
                'train': {'total': 60, 'hit': 39, 'success_rate': 0.65},
                'flight': {'total': 60, 'hit': 45, 'success_rate': 0.75},
                'weather': {'total': 90, 'hit': 84, 'success_rate': 0.9333333333333333},
                'movie': {'total': 60, 'hit': 20, 'success_rate': 0.3333333333333333},
                'tv': {'total': 60, 'hit': 24, 'success_rate': 0.4},
                'hospital': {'total': 38, 'hit': 23, 'success_rate': 0.6052631578947368},
                'pc': {'total': 37, 'hit': 26, 'success_rate': 0.7027027027027027},
                'car': {'total': 38, 'hit': 20, 'success_rate': 0.5263157894736842},
                'class': {'total': 37, 'hit': 20, 'success_rate': 0.5405405405405406},
                'Averaged_task_success': 67.38095238095238,
            },
        ),
    ]
)

diff = list(dictdiffer.diff(results, gold_results))
print('diff: ', diff)
assert len(diff) == 0
