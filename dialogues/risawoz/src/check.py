import argparse
import itertools
import json
import os
import pymongo
import requests
import sys

from collections import defaultdict
from contextlib import ExitStack
from pathlib import Path

from tqdm.autonotebook import tqdm

parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, default='dialogues/risawoz/',
                    help='code root directory')
parser.add_argument("--data_dir", type=str, default="data/original/",
                    help="path to original data, relative to root dir")
parser.add_argument("--save_dir", type=str, default="data/",
                    help="path to save preprocessed data, relative to root dir")
parser.add_argument("--src", type=str, help="en, zh, en_zh", default="zh")
parser.add_argument("--tgt", type=str, help="en, fr", default="en")
parser.add_argument("--setting", type=str, help="en, fr, zh, en_zh")
parser.add_argument("--splits", nargs='+', default=['fewshot', 'valid', 'test'])
parser.add_argument("--debug", action="store_true", help="toggle debug mode")
args = parser.parse_args()


def check(turn, domain, slot):
    turn_id = turn["turn_id"]
    turn_domain = turn["turn_domain"][0].lower()
    if turn_domain != domain.lower():
        return
    if (domain in turn["turn_domain"]
            and len(turn["db_results"]) > 1
            and slot in turn["db_results"][1]):
        # breakpoint()
        # db_type = turn["db_results"][1]["type"]
        db_consumption = turn["db_results"][1][slot]
        possible_values = []
        if db_consumption in mapping[turn_domain][slot]:
            possible_values = mapping[turn_domain][slot][
                db_consumption]
        else:
            for consumption_type in mapping[turn_domain][slot]:
                if db_consumption in mapping[turn_domain][slot][consumption_type]:
                    possible_values = mapping[turn_domain][slot][consumption_type]
                    break

        if db_consumption not in possible_values:
            possible_values.append(db_consumption)
        if f"{domain}-{slot}" in turn["belief_state"][
                "inform slot-values"]:
            if "turn_inform" in turn:
                inform = turn["turn_inform"][f"{domain}-{slot}"]
                if inform not in possible_values:
                    print(f"{split}, {dialog_id}, turn {turn_id}: "
                          f"db: {db_consumption}, inform: {inform}",
                          file=sys.stderr)
                    turn["turn_inform"][
                        f"{domain}-{slot}"] = db_consumption
            slot_value = turn["belief_state"]["inform slot-values"][
                f"{domain}-{slot}"]
            if slot_value not in possible_values:
                print(f"{split}, {dialog_id}, turn {turn_id}: "
                      f"db: {db_consumption}, value: {slot_value}", file=sys.stderr)
                turn["belief_state"]["inform slot-values"][
                    f"{domain}-{slot}"] = db_consumption


if __name__ == "__main__":
    with open(f"{args.root}/src/knowledgebase/mappings/"
              f"{args.src}2canonical.json") as mapping_file:
        mapping = json.load(mapping_file)
    processed_data_path = os.path.join(*[args.root, args.save_dir])
    for split in args.splits:
        print(f"processing {split} data...")
        with open(f"{args.root}/{args.data_dir}/{args.src}_{split}.json") as data_file:
            data = json.load(data_file)
            for dialog in tqdm(data):
                dialog_id = dialog["dialogue_id"]
                dialogue = dialog["dialogue"]
                for turn in dialogue:
                    check(turn, "Attraction", "consumption")
                    # check(turn, "Restaurant", "cuisine")

        with open(f"{args.root}/{args.data_dir}/{args.src}_{split}.json.new", "w",
                  encoding='utf8') as data_file:
            json.dump(data, data_file, indent=4, ensure_ascii=False)
