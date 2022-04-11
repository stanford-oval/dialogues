import argparse

from dialogues import Bitod

parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, help='data root directory')
parser.add_argument("--save_dir", type=str, default="data/preprocessed", help="path to save prerpocessed data for training")
parser.add_argument("--setting", type=str, default="zh", help="en, zh, en_zh, en2zh, zh2en")
parser.add_argument("--nlg", action='store_true', help="only keep agent side (for nlg)")
parser.add_argument(
    "--pretraining_prefix", type=str, default="", help="for cross lingual pretrainings: [en2zh_trainsfer, zh2en_trainsfer]"
)
parser.add_argument("--max_history", type=int, default=0)
parser.add_argument("--splits", nargs='+', default=['train', 'eval', 'test'])
parser.add_argument("--dataset", choices=["bitod", "risawoz", "multiwoz"], default="risawoz")
parser.add_argument("--version", type=int)
parser.add_argument("--fewshot_percent", type=int, default="10")
parser.add_argument("--gen_full_state", default=True)
parser.add_argument("--use_user_acts", default=True)
parser.add_argument("--english_slots", default=False)
parser.add_argument('--better_history_boundary', default=True)
parser.add_argument("--gen_lev_span", default=True)
parser.add_argument("--add_end_tokens", default=True)
parser.add_argument("--last_two_agent_turns", default=True)
parser.add_argument("--use_natural_response", default=True)
parser.add_argument("--no_state", default=True)
parser.add_argument("--add_api_results", default=True)
parser.add_argument("--simpletod", default=True)
parser.add_argument("--only_gen_natural_response", default=True)
parser.add_argument("--four_steps", default=True)
parser.add_argument("--no_reset_api", default=True)
parser.add_argument("--drop_user_api_da", default=True)
parser.add_argument("--only_user_rg", default=True)
parser.add_argument("--sampling", choices=["random", "balanced"], default="random")

args = parser.parse_args()

if args.dataset == "risawoz":
    # temporary test setting since translation is not ready
    args.english_slots = False
    args.setting = "zh"
    args.fewshot_percent = 1
    args.root = "../../risawoz"

dataset = Bitod()
train, fewshot, dev, test = dataset.process_data(args, args.root)
print(len(dev))
