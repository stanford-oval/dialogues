import argparse

from dialogues import Bitod

parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, help='data root directory')
parser.add_argument("--save_dir", type=str, default="data/preprocessed", help="path to save prerpocessed data for training")
parser.add_argument("--setting", type=str, default="en", help="en, zh, en_zh, en2zh, zh2en")
parser.add_argument("--splits", nargs='+', default=['train', 'eval', 'test'])
parser.add_argument("--version", type=int)
parser.add_argument("--fewshot_percent", type=int, default="10")

args = parser.parse_args()

dataset = Bitod()
train, fewshot, dev, test = dataset.process_data(args, args.root)
print(len(dev))
