import argparse
import os
from collections import OrderedDict

import dictdiffer

from dialogues import Bitod

parser = argparse.ArgumentParser()

parser.add_argument("--reference_file_path", type=str, default="dialogues/bitod/data/en_test.json", help="path of reference")
parser.add_argument(
    "--prediction_file_path", type=str, default="dialogues/bitod/results/test/bitod_preds.json", help="path of prediction"
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

dataset = Bitod()
dataset.FAST_EVAL = True
results = dataset.compute_metrics(args, args.prediction_file_path, args.reference_file_path)
gold_results = OrderedDict(
    [
        ('bleu', 41.1513),
        ('ser', 12.531101560732866),
        ('success_rate', 49.7737556561086),
        ('api_acc', 78.1303602058319),
        ('da_acc', 62.72336575435422),
        ('jga', 78.96403528613436),
        (
            'task_info',
            {
                'hotels_en_US_search': {'total': 199, 'hit': 151, 'success_rate': 0.7587939698492462},
                'hotels_en_US_booking': {'total': 194, 'hit': 180, 'success_rate': 0.9278350515463918},
                'attractions_en_US_search': {'total': 235, 'hit': 151, 'success_rate': 0.6425531914893617},
                'HKMTR_en': {'total': 147, 'hit': 109, 'success_rate': 0.7414965986394558},
                'restaurants_en_US_booking': {'total': 166, 'hit': 123, 'success_rate': 0.7409638554216867},
                'restaurants_en_US_search': {'total': 205, 'hit': 106, 'success_rate': 0.5170731707317073},
                'weathers_en_US_search': {'total': 20, 'hit': 20, 'success_rate': 1.0},
                'Averaged_task_success': 72.04116638078902,
            },
        ),
    ]
)

print('diff: ', list(dictdiffer.diff(results, gold_results)))
