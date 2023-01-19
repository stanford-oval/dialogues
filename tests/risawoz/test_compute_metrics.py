import argparse
import os
from collections import OrderedDict

import dictdiffer

from dialogues import Risawoz

parser = argparse.ArgumentParser()

parser.add_argument("--eval_task", type=str, default="end2end", help="end2end, dst, response")
parser.add_argument("--setting", type=str, help="en, zh, en&zh, en2zh, zh2en")
parser.add_argument("--result_path", type=str, default="./", help="result_path")
parser.add_argument("--save_prefix", type=str, default="", help="prefix of save file name")

args = parser.parse_args()

if not os.path.exists(args.result_path):
    os.makedirs(args.result_path)

# TODO add tests for en
args.setting = 'zh'
reference_file_path = f'./tests/risawoz/data/{args.setting}/converted_valid.json'
prediction_file_path = f'tests/risawoz/data/{args.setting}/preds.json'

dataset = Risawoz()
dataset.FAST_EVAL = True

results = dataset.compute_metrics(args, prediction_file_path, reference_file_path)

# api, da, and ser are not correct
gold_results = OrderedDict(
    [
        ('bleu', 46.0123),
        ('ser', 18.506653523903402),
        ('success_rate', 56.166666666666664),
        ('api_acc', 83.27485380116958),
        ('da_acc', 79.07836372597339),
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
                'pc': {'total': 37, 'hit': 24, 'success_rate': 0.6486486486486487},
                'car': {'total': 38, 'hit': 20, 'success_rate': 0.5263157894736842},
                'class': {'total': 37, 'hit': 8, 'success_rate': 0.21621621621621623},
                'Averaged_task_success': 65.71428571428571,
            },
        ),
    ]
)

print(results)

diff = list(dictdiffer.diff(results, gold_results))
print('diff: ', diff)
assert len(diff) == 0
