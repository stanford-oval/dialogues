import argparse

from dialogues import Bitod

parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, default='dialogues/bitod/', help='data root directory')
parser.add_argument("--data_dir", type=str, default="data", help="path to save original data, relative to root dir")
parser.add_argument("--save_dir", type=str, default="data/preprocessed", help="path to save prerpocessed data for training")
parser.add_argument("--setting", type=str, default="en", help="en, zh, en_zh, en2zh, zh2en")
parser.add_argument("--splits", nargs='+', default=['train', 'valid', 'test'])
parser.add_argument("--version", type=int)
parser.add_argument("--max_history", type=int, default=2)
parser.add_argument("--fewshot_percent", type=int, default=0)
parser.add_argument("--sampling", choices=["sequential", "balanced"], default="sequential")
parser.add_argument("--use_user_acts", action='store_true')
parser.add_argument("--gen_lev_span", action='store_true')
parser.add_argument("--gen_full_state", action='store_true')
parser.add_argument("--last_two_agent_turns", action='store_true')
parser.add_argument("--english_slots", action='store_true')
parser.add_argument("--use_natural_response", action='store_true')
parser.add_argument("--only_user_rg", action='store_true')

args = parser.parse_args()

dataset = Bitod()
train, fewshot, dev, test = dataset.process_data(args)
print(len(dev))
