import argparse
import itertools
import json
import os
from collections import defaultdict
from contextlib import ExitStack
from pathlib import Path

import pymongo
import requests
from genienlp.data_utils.almond_utils import is_cjk_char
from tqdm.autonotebook import tqdm

from dialogues import Risawoz
from dialogues.risawoz.src.knowledgebase.api import call_api

dataset = Risawoz()


def read_json_files_in_folder(path):
    json_filename = [path + '/' + filename for filename in os.listdir(path) if '.json' in filename]
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in json_filename]
        data = {}
        for i in range(len(files)):
            data[Path(json_filename[i]).stem] = json.load(files[i])
    return data


def build_db(db_json_path, api_map=None, mongodb_host="", setting='zh_CN'):
    if setting == 'zh':
        setting = 'zh_CN'
    raw_db = read_json_files_in_folder(db_json_path)
    if mongodb_host:
        db_client = pymongo.MongoClient(mongodb_host)
    else:
        db_client = pymongo.MongoClient()
    risawoz_db = db_client["risawoz"]
    for db in risawoz_db.list_collection_names():
        risawoz_db[db].drop()
    for domain in raw_db.keys():
        if api_map is None:
            col = risawoz_db[domain]
        else:
            col = risawoz_db[api_map[domain.split(f"_{setting}")[0]]]
        for i in range(len(raw_db[domain])):
            slot_list = list(raw_db[domain][i].keys())
            for s in slot_list:
                if "." in s:
                    # escape dot cause mongodb doesn't like '.' and '$' in key names
                    raw_db[domain][i][s.replace(".", "\uFF0E")] = raw_db[domain][i].pop(s)
        col.insert_many(raw_db[domain], ordered=True)
    return risawoz_db


def tokenize_string(sentence):
    output = []
    i = 0
    while i < len(sentence):
        output.append(sentence[i])
        if is_cjk_char(ord(sentence[i])) and i + 1 < len(sentence) and not is_cjk_char(ord(sentence[i + 1])):
            output.append(' ')
        elif not is_cjk_char(ord(sentence[i])) and i + 1 < len(sentence) and is_cjk_char(ord(sentence[i + 1])):
            output.append(' ')
        i += 1

    output = "".join(output)
    output = output.replace('  ', ' ')

    return output


def process_string(sentence):
    if not isinstance(sentence, str):
        return sentence
    sentence = ''.join(sentence.split())
    sentence = tokenize_string(sentence)

    return sentence


#
#
# def tokenize_string(sentence):
#     output = []
#     i = 0
#     while i < len(sentence):
#         output.append(sentence[i])
#         if is_cjk_char(ord(sentence[i])):
#             is_split = True
#             j = i + 1
#             while j < len(sentence):
#                 if not re.fullmatch('[0-9:]', sentence[j]):
#                     is_split = False
#                     break
#                 j += 1
#
#             if is_split:
#                 output.append(' ')
#         i += 1
#
#     output = "".join(output)
#     output = output.replace('  ', ' ')
#
#     return output
#
#
# def process_val(val, slot):
#     val = ''.join(val.split())
#
#     if slot in ['教室地点']:
#         continue
#
#     val = tokenize_string(val)
#
#     return val


def group_slot_values(actions):
    # group slot values in user/system actions with same act-domain-slot prefix
    for i in range(len(actions)):
        actions[i][0] = actions[i][0].strip()  # strip spaces of ' inform '
    processed_actions = []
    grouped_actions = [list(v) for _, v in itertools.groupby(sorted(actions), lambda x: x[:3])]
    for group in grouped_actions:
        # TODO: the ''.join will cause mismatches between entities in input and output annotations
        # delete spaces and replace "" into []
        for i in range(len(group)):
            if group[i][3]:
                # keep space between cjk and other chars
                group[i][3] = [process_string(group[i][3])]
            else:
                group[i][3] = []
        if len(group) == 1:
            group = group[0]  # squeeze
        else:
            group = group[0][:3] + [[action[3] for action in group]]
        processed_actions.append(group)
    return processed_actions


def build_user_event(turn):
    event = {"Agent": "User"}
    # actions
    # TODO: handle domain information
    action_seq = ["act", "domain", "slot", "value"]
    actions = []
    processed_original_actions = group_slot_values(turn["user_actions"])
    for action in processed_original_actions:
        event_action = {}
        for i in range(len(action)):
            event_action[action_seq[i]] = action[i]
        if event_action["slot"] and event_action["value"]:
            event_action["relation"] = "等于"
        else:
            event_action["relation"] = ""
        event_action["active_intent"] = event_action["domain"]
        actions.append(event_action)
    event["Actions"] = actions
    # TODO: handle multiple active intents
    event["active_intent"] = turn["turn_domain"]
    event["state"] = defaultdict(dict)
    for ds, v in turn["belief_state"]["inform slot-values"].items():
        d, s = ds.split("-")[0], ds.split("-")[1]
        event["state"][d][s] = {"relation": "等于", "value": [process_string(v)]}
    event["state"] = dict(event["state"])
    # event["Text"] = turn["user_utterance"]
    event["Text"] = process_string(turn["segmented_user_utterance"])
    return event


def build_wizard_event(turn, mode="normal"):
    assert mode in ["normal", "query"]
    event = {"Agent": "Wizard"}
    if mode == "query":
        event["Actions"] = "query"
        event["Constraints"] = defaultdict(dict)
        event["Constraints_raw"] = defaultdict(dict)
        for ds, v in turn["belief_state"]["inform slot-values"].items():
            # only return matched result in the domains of current turn
            d, s = ds.split("-")
            # if d in turn["turn_domain"]:
            event["Constraints"][d][s] = process_string(v)
            event["Constraints_raw"][d][s] = ''.join(v.split())
        # TODO: handle multiple APIs
        event["API"] = list(set([d for d in event["Constraints"].keys()]))
    else:
        # actions
        action_seq = ["act", "domain", "slot", "value"]
        actions = []
        processed_original_actions = group_slot_values(turn["system_actions"])
        for action in processed_original_actions:
            event_action = {}
            for i in range(len(action)):
                event_action[action_seq[i]] = action[i]
            event_action["relation"] = "等于" if event_action["slot"] and event_action["value"] else ""
            actions.append(event_action)
        event["Actions"] = actions

        # event["Text"] = turn["system_utterance"]
        event["Text"] = process_string(turn["segmented_system_utterance"])
    return event


def build_kb_event(wizard_query_event, db, actions):
    event = {"Agent": "KnowledgeBase"}
    constraints = wizard_query_event["Constraints_raw"]
    api_names = wizard_query_event["API"]
    knowledge = call_api(db, api_names, constraints, lang='zh_CN', value_mapping=dataset.value_mapping, actions=actions)
    event["TotalItems"] = sum(item.get("available_options", 0) for api, item in knowledge.items())
    for api, item in knowledge.items():
        for slot, val in item.items():
            knowledge[api][slot] = process_string(val)
    event["Item"] = knowledge
    event["Topic"] = api_names
    return event


def build_dataset(original_data_path, db):
    with open(original_data_path) as fin:
        data = json.load(fin)
    processed_data = {}
    for dialogue in tqdm(data):
        dialogue_id = dialogue["dialogue_id"]
        scenario = {
            "UserTask": dialogue.get("goal", ""),
            "WizardCapabilities": [{"Task": domain} for domain in dialogue["domains"]],
        }
        events = []
        for turn in dialogue["dialogue"]:
            user_turn_event = build_user_event(turn)
            if "db_results" in turn and turn["db_results"]:
                wizard_query_event = build_wizard_event(turn, mode="query")
                wizard_normal_event = build_wizard_event(turn, mode="normal")

                actions = defaultdict(defaultdict)
                for act in wizard_normal_event['Actions']:
                    domain, slot, value = act['domain'], act['slot'], act['value']
                    if slot:
                        actions[domain][slot] = value

                kb_event = build_kb_event(wizard_query_event, db, actions)

                # del wizard_query_event['Constraints_raw']
                events += [user_turn_event, wizard_query_event, kb_event, wizard_normal_event]
            else:
                wizard_event = build_wizard_event(turn)
                events += [user_turn_event, wizard_event]
        processed_data[dialogue_id] = {"Dialogue_id": dialogue_id, "Scenario": scenario, "Events": events}
    return processed_data


# def build_mock_pred_data(test_data_path):
#     with open(test_data_path, 'r') as f:
#         test_data = json.load(f)
#     fake_pred_data = {}
#     for dialog in test_data:
#         fake_pred_dialog = {"turns": {}}
#         final_dialog_state = {}
#         for turn in dialog["dialogue"]:
#             fake_pred_dialog["turns"][str(turn["turn_id"] + 1)] = {"response": [turn["system_utterance"]]}
#             # build dialog state
#             dialog_state = {}
#             for ds, v in turn["belief_state"]["inform slot-values"].items():
#                 v = ''.join(v.split())
#                 d, s = ds.split("-")
#                 if d in dialog_state.keys():
#                     if s in dialog_state[d].keys():
#                         dialog_state[d][s]["value"].append(v)
#                     else:
#                         dialog_state[d][s] = {}
#                         dialog_state[d][s]["relation"] = "等于"
#                         dialog_state[d][s]["value"] = [v]
#                 else:
#                     dialog_state[d] = {}
#                     dialog_state[d][s] = {}
#                     dialog_state[d][s]["relation"] = "等于"
#                     dialog_state[d][s]["value"] = [v]
#             fake_pred_dialog["turns"][str(turn["turn_id"] + 1)]["state"] = copy.deepcopy(dialog_state)
#             # update final dialog state in each turn and build turn API text
#             turn_api_text = []
#             for d, sv in dialog_state.items():
#                 if d in final_dialog_state.keys():
#                     final_dialog_state[d].update(sv)
#                 else:
#                     final_dialog_state[d] = sv
#                 # build turn API text
#                 try:
#                     if len(turn["db_results"]) > 1:
#                         first_result = eval(turn["db_results"][1].replace("true", "True").replace("false", "False"))
#                         turn_domain_api_text = f"( {d} ) "
#                         for s, v in first_result.items():
#                             turn_domain_api_text += f"{s} \" {v} \" , "
#                         turn_api_text.append(turn_domain_api_text[:-3])
#                 except:
#                     print(turn["db_results"])
#             fake_pred_dialog["turns"][str(turn["turn_id"] + 1)]["api"] = [' '.join(turn_api_text)]
#             # build actions
#             turn_action_domain_list = [action[1] for action in turn["system_actions"]]
#             turn_action_text = [f"( {d} ) " for d in turn_action_domain_list]
#             for action in turn["system_actions"]:
#                 for i in range(len(turn_action_domain_list)):
#                     if action[1] == turn_action_domain_list[i]:
#                         if action[0].strip() == "Inform" or action[3]:
#                             val = ''.join(action[3].split())
#                             turn_action_text[i] += f"{action[0].strip().lower()} {action[2]} 等于 \" {val} \" , "
#                         # elif action[3]:
#                         #     turn_action_text[
#                         #         i
#                         #     ] += f"{action[0].strip().lower()} {action[2]} \" {''.join(action[3].split())} \" , "
#                         else:
#                             turn_action_text[i] += f"{action[0].strip().lower()} {action[2]} , "
#             turn_action_text = [text[:-3] for text in turn_action_text]
#             fake_pred_dialog["turns"][str(turn["turn_id"] + 1)]["actions"] = [' '.join(turn_action_text)]
#         fake_pred_dialog["API"] = copy.deepcopy(final_dialog_state)
#         fake_pred_data[dialog["dialogue_id"]] = copy.deepcopy(fake_pred_dialog)
#     return fake_pred_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--root", type=str, default='dialogues/risawoz/', help='code root directory')
    parser.add_argument("--data_dir", type=str, default="data/original", help="path to original data, relative to root dir")
    parser.add_argument("--save_dir", type=str, default="data/", help="path to save preprocessed data, relative to root dir")
    parser.add_argument("--setting", type=str, default="en", help="en, zh, en_zh")
    parser.add_argument("--splits", nargs='+', default=['train', 'valid', 'test'])

    args = parser.parse_args()

    mongodb_host = "mongodb://localhost:27017/"

    # uncomment to build db
    risawoz_db = build_db(
        db_json_path=os.path.join(*[args.root, 'database/db']), api_map=None, mongodb_host=mongodb_host, setting=args.setting
    )

    # download original RiSAWOZ dataset
    original_data_path = os.path.join(*[args.root, args.data_dir])
    for split in args.splits:
        if not os.path.exists(os.path.join(original_data_path, f"{args.setting}_{split}.json")):
            os.makedirs(original_data_path, exist_ok=True)
            print(f"{split} set is not found, downloading...")
            if split == "valid":
                data_url = "https://huggingface.co/datasets/GEM/RiSAWOZ/resolve/main/dev.json"
            else:
                data_url = f"https://huggingface.co/datasets/GEM/RiSAWOZ/resolve/main/{split}.json"
            with open(f"{original_data_path}/{split}.json", 'wb') as f:
                f.write(requests.get(data_url).content)

    processed_data_path = os.path.join(*[args.root, args.save_dir])
    for split in args.splits:
        print(f"processing {split} data...")
        processed_data = build_dataset(os.path.join(original_data_path, f"{args.setting}_{split}.json"), db=risawoz_db)
        # save converted files in JSON format
        with open(f"{processed_data_path}/{args.setting}_{split}.json", 'w') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

    # # generating mock prediction data
    # print("generating mock prediction data...")
    # mock_pred_data = build_mock_pred_data(os.path.join(args.root, "./data/original/zh_test.json"))
    # with open(os.path.join(args.root, "./results/test/risawoz_mock_preds.json"), "w") as f:
    #     json.dump(mock_pred_data, f, ensure_ascii=False, indent=4)
