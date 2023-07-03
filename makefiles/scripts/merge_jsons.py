import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--input_files', nargs='+')
parser.add_argument('--output_file')

args = parser.parse_args()

data = {}
for file in args.input_files:
    with open(file) as fin:
        data.update(json.load(fin))

with open(args.output_file, 'w') as fout:
    json.dump(data, fout)
