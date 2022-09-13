import argparse
import itertools
import json
import os
from collections import defaultdict
from contextlib import ExitStack
from pathlib import Path

import pymongo
import requests
from tqdm.autonotebook import tqdm

from dialogues.risawoz.main import Risawoz
from dialogues.risawoz.src.knowledgebase.api import call_api, process_string

dataset = Risawoz()


def read_json_files_in_folder(path):
    json_filename = [path + '/' + filename for filename in os.listdir(path) if '.json' in filename]
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in json_filename]
        data = {}
        for i in range(len(files)):
            data[Path(json_filename[i]).stem] = json.load(files[i])
    return data


def build_db(db_json_path, api_map, setting, mongodb_host=""):
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


def group_slot_values(actions, setting):
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
                group[i][3] = [process_string(group[i][3], setting)]
            else:
                group[i][3] = []
        if len(group) == 1:
            group = group[0]  # squeeze
        else:
            group = group[0][:3] + [[action[3] for action in group]]
        processed_actions.append(group)
    return processed_actions


def build_user_event(turn, setting):
    event = {"Agent": "User"}
    # actions
    # TODO: handle domain information
    action_seq = ["act", "domain", "slot", "value"]
    actions = []
    processed_original_actions = group_slot_values(turn["user_actions"], setting)
    for action in processed_original_actions:
        event_action = {}
        for i in range(len(action)):
            if i == 1 and action[i]:
                action[i] = dataset.value_mapping.zh2en_DOMAIN_MAP.get(action[i], action[i].lower())
            elif i == 2 and action[i]:
                action[i] = dataset.value_mapping.zh2en_SLOT_MAP.get(action[i], action[i])
            elif i == 3 and action[i]:
                action[i] = process_string(action[i], setting)
            event_action[action_seq[i]] = action[i]
        if event_action["slot"] and event_action["value"]:
            event_action["relation"] = "equal_to"
        else:
            event_action["relation"] = ""
        event_action["active_intent"] = event_action["domain"]
        actions.append(event_action)
    event["Actions"] = actions
    # TODO: handle multiple active intents
    event["active_intent"] = [dataset.value_mapping.zh2en_DOMAIN_MAP.get(dom, dom) for dom in turn["turn_domain"]]
    event["state"] = defaultdict(dict)
    for ds, v in turn["belief_state"]["inform slot-values"].items():
        d, s = ds.split("-")[0], ds.split("-")[1]
        d = dataset.value_mapping.zh2en_DOMAIN_MAP.get(d, d)
        s = dataset.value_mapping.zh2en_SLOT_MAP.get(s, s)
        event["state"][d][s] = {"relation": "equal_to", "value": [process_string(v, setting)]}
    event["state"] = dict(event["state"])
    # event["Text"] = turn["user_utterance"]
    event["Text"] = process_string(turn["user_utterance"], setting)
    return event


def build_wizard_event(turn, setting, mode="normal"):
    assert mode in ["normal", "query"]
    event = {"Agent": "Wizard"}
    turn_domain_en = [dataset.value_mapping.zh2en_DOMAIN_MAP.get(d, d.lower()) for d in turn['turn_domain']]
    if mode == "query":
        event["Actions"] = "query"
        event["Constraints"] = defaultdict(dict)
        # event["Constraints_raw"] = defaultdict(dict)
        for ds, v in turn["belief_state"]["inform slot-values"].items():
            # only return matched result in the domains of current turn
            d, s = ds.split("-")
            d = dataset.value_mapping.zh2en_DOMAIN_MAP.get(d, d.lower())
            s = dataset.value_mapping.zh2en_SLOT_MAP.get(s, s)
            if d in turn_domain_en:
                event["Constraints"][d][s] = process_string(v, setting)
            # event["Constraints_raw"][d][s] = ''.join(v.split())
        # TODO: handle multiple APIs
        event["API"] = list(set([d for d in event["Constraints"].keys()]))
        if not event["API"]:
            event["API"] = turn_domain_en
    else:
        # actions
        action_seq = ["act", "domain", "slot", "value"]
        actions = []
        processed_original_actions = group_slot_values(turn["system_actions"], setting)
        for action in processed_original_actions:
            event_action = {}
            for i in range(len(action)):
                if i == 1 and action[i]:
                    action[i] = dataset.value_mapping.zh2en_DOMAIN_MAP.get(action[i], action[i].lower())
                elif i == 2 and action[i]:
                    action[i] = dataset.value_mapping.zh2en_SLOT_MAP.get(action[i], action[i])
                elif i == 3 and action[i]:
                    action[i] = process_string(action[i], setting)
                event_action[action_seq[i]] = action[i]
            event_action["relation"] = "equal_to" if event_action["slot"] and event_action["value"] else ""
            actions.append(event_action)
        event["Actions"] = actions

        # event["Text"] = turn["system_utterance"]
        event["Text"] = process_string(turn["system_utterance"], setting)
    return event


def build_kb_event(wizard_query_event, db, actions, expected_num_results, setting):
    event = {"Agent": "KnowledgeBase"}
    constraints = wizard_query_event["Constraints"]
    for d in constraints:
        constraints[d] = {k.replace(" ", "_"): v for k, v in constraints[d].items()}
    api_names = wizard_query_event["API"]
    knowledge = call_api(db, api_names, constraints, lang=setting, value_mapping=dataset.value_mapping, actions=actions)
    event["TotalItems"] = sum(item.get("available_options", 0) for api, item in knowledge.items())
    # if event["TotalItems"] == 0 and not expected_num_results == 0:
    # if event["TotalItems"] < expected_num_results and api_names != ['general']:
    for api, item in knowledge.items():
        if item.get("available_options", 0) < expected_num_results and api_names != ['general']:
            print('API call likely failed')
            knowledge = call_api(db, api_names, constraints, lang='zh', value_mapping=dataset.value_mapping, actions=actions)

    # for api, item in knowledge.items():
    #     for slot, val in item.items():
    #         knowledge[api][slot] = process_string(val, setting)
    event["Item"] = knowledge
    event["Topic"] = api_names
    return event


def build_dataset(original_data_path, db, setting):
    with open(original_data_path) as fin:
        data = json.load(fin)
    processed_data = {}
    for dialogue in tqdm(data):
        dialogue_id = dialogue["dialogue_id"]
        scenario = {
            "UserTask": dialogue.get("goal", ""),
            "WizardCapabilities": [
                {"Task": dataset.value_mapping.zh2en_DOMAIN_MAP.get(domain, domain.lower())} for domain in dialogue["domains"]
            ],
        }
        events = []
        turn_id = 0
        for turn in dialogue["dialogue"]:
            user_turn_event = build_user_event(turn, setting)
            if "db_results" in turn and turn["db_results"]:
                wizard_query_event = build_wizard_event(turn, setting, mode="query")
                wizard_normal_event = build_wizard_event(turn, setting, mode="normal")

                actions = defaultdict(defaultdict)
                for act in wizard_normal_event['Actions']:
                    domain, slot, value = act['domain'], act['slot'], act['value']
                    if slot:
                        actions[domain][slot] = value
                if setting == 'zh':
                    expected_num_results = int(turn["db_results"][0][len('数据库检索结果：成功匹配个数为') :])
                else:
                    expected_num_results = int(
                        turn["db_results"][0][len('Database search results: the number of successful matches is ') :]
                    )

                kb_event = build_kb_event(wizard_query_event, db, actions, expected_num_results, setting)
                user_turn_event['turn_id'] = turn_id
                wizard_query_event['turn_id'] = turn_id
                wizard_normal_event['turn_id'] = turn_id
                # del wizard_query_event['Constraints_raw']
                events += [user_turn_event, wizard_query_event, kb_event, wizard_normal_event]
            else:
                wizard_event = build_wizard_event(turn, setting)
                user_turn_event['turn_id'] = turn_id
                wizard_event['turn_id'] = turn_id
                events += [user_turn_event, wizard_event]

            turn_id += 1
        processed_data[dialogue_id] = {"Dialogue_id": dialogue_id, "Scenario": scenario, "Events": events}
    return processed_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--root", type=str, default='dialogues/risawoz/', help='code root directory')
    parser.add_argument("--data_dir", type=str, default="data/original/", help="path to original data, relative to root dir")
    parser.add_argument("--save_dir", type=str, default="data/", help="path to save preprocessed data, relative to root dir")
    parser.add_argument("--setting", type=str, default="en", help="en, zh, en_zh")
    parser.add_argument("--splits", nargs='+', default=['train', 'valid', 'test'])

    args = parser.parse_args()

    mongodb_host = "mongodb://localhost:27017/"

    # uncomment to build db
    risawoz_db = build_db(
        db_json_path=os.path.join(*[args.root, f'database/db_{args.setting}']),
        api_map=None,
        setting=args.setting,
        mongodb_host=mongodb_host,
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
            with open(f"{original_data_path}/{args.setting}_{split}.json", 'wb') as f:
                f.write(requests.get(data_url).content)

    processed_data_path = os.path.join(*[args.root, args.save_dir])
    for split in args.splits:
        print(f"processing {split} data...")
        processed_data = build_dataset(
            os.path.join(original_data_path, f"{args.setting}_{split}.json"), risawoz_db, args.setting
        )
        # save converted files in JSON format
        with open(f"{processed_data_path}/{args.setting}_{split}.json", 'w') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
