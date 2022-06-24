import argparse

from dialogues import Multiwoz24

parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, help='data root directory')
parser.add_argument("--version", type=int)

args = parser.parse_args()

dataset = Multiwoz24()
train, dev, test = dataset.process_data(args, args.root)
print(len(dev))
