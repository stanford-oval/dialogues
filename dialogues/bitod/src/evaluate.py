import argparse
import json
import os

from dialogues.bitod.main import Bitod


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference_file_path", type=str, default="data/test.json", help="path of reference")
    parser.add_argument("--prediction_file_path", type=str, help="path of prediction")
    parser.add_argument("--setting", type=str, default="en", help="en, zh, en&zh, en2zh, zh2en")
    parser.add_argument("--result_path", type=str, default="./", help="eval_model or eval_file?")
    parser.add_argument("--save_prefix", type=str, default="", help="prefix of save file name")

    args = parser.parse_args()

    dataset = Bitod()

    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)

    results = dataset.eval_file(args, args.prediction_file_path, args.reference_file_path)

    with open(os.path.join(args.result_path, f"{args.save_prefix}{args.setting}_result.json"), "w") as f:
        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
