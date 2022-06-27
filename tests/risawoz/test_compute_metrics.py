import argparse
import os
from collections import OrderedDict

import dictdiffer

from dialogues import Risawoz

parser = argparse.ArgumentParser()

parser.add_argument("--reference_file_path", type=str, default="dialogues/risawoz/data/zh_test.json", help="path of reference")
parser.add_argument(
    "--prediction_file_path",
    type=str,
    default="dialogues/risawoz/results/test/risawoz_mock_preds.json",
    help="path of prediction",
)
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
        ('bleu', 100.0),
        ('ser', 16.347189317251775),
        ('success_rate', 100.0),
        ('api_acc', 0.0),
        ('da_acc', 46.090889511091966),
        ('jga', 100.0),
        (
            'task_info',
            {
                '旅游景点': {'total': 103, 'hit': 103, 'success_rate': 1.0},
                '餐厅': {'total': 99, 'hit': 99, 'success_rate': 1.0},
                '酒店': {'total': 112, 'hit': 112, 'success_rate': 1.0},
                '火车': {'total': 78, 'hit': 78, 'success_rate': 1.0},
                '飞机': {'total': 75, 'hit': 75, 'success_rate': 1.0},
                '天气': {'total': 99, 'hit': 99, 'success_rate': 1.0},
                '电影': {'total': 78, 'hit': 78, 'success_rate': 1.0},
                '电视剧': {'total': 78, 'hit': 78, 'success_rate': 1.0},
                '医院': {'total': 47, 'hit': 47, 'success_rate': 1.0},
                '电脑': {'total': 47, 'hit': 47, 'success_rate': 1.0},
                '汽车': {'total': 33, 'hit': 33, 'success_rate': 1.0},
                '辅导班': {'total': 46, 'hit': 46, 'success_rate': 1.0},
                'Averaged_task_success': 100.0,
            },
        ),
    ]
)

print('diff: ', list(dictdiffer.diff(results, gold_results)))
