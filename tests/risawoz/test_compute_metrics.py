import argparse
import os

from dialogues import Risawoz

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--reference_file_path", type=str, default="../../risawoz/data/zh_test.json", help="path of reference")
    parser.add_argument(
        "--prediction_file_path", type=str, default="../../risawoz/results/test/risawoz_preds.json", help="path of prediction"
    )
    parser.add_argument("--eval_task", type=str, default="end2end", help="end2end, dst, response")
    parser.add_argument("--setting", type=str, help="en, zh, en&zh, en2zh, zh2en", default="zh")
    parser.add_argument("--result_path", type=str, default="./", help="eval_model or eval_file?")
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
    results = dataset.compute_metrics(args, args.prediction_file_path, args.reference_file_path)

    print(results)
