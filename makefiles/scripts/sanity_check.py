import argparse
import json

parser = argparse.ArgumentParser()

parser.add_argument('--input_file')

args = parser.parse_args()

pos, neg = 0, 0

with open(args.input_file) as fin:
    file = json.load(fin)
    for dial in file['data']:
        if dial['train_target'] != 'dst':
            continue

        if dial['category'] == 'positive':
            pos += 1
        else:
            neg += 1

print(f'neg: {neg}, pos: {pos}')
#
# with open(args.input_file) as fin:
#     gold_neg_count = 0
#     pred_neg_count = 0
#     recall = 0.0
#     precision = 0.0
#
#     for line in fin:
#         id_, pred, gold, sent = line.strip('\n').split('\t')
#
#         if gold == 'negative':
#             gold_neg_count += 1
#             if pred == 'negative':
#                 recall += 1
#
#         if pred == 'negative':
#             pred_neg_count += 1
#             if gold == 'negative':
#                 precision += 1
#
#     print(f'recall: {recall/ gold_neg_count}, precision: {precision/ pred_neg_count}')
