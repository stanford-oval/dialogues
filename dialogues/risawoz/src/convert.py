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


def read_json_files_in_folder(path):
    json_filename = [path + '/' + filename for filename in os.listdir(path) if '.json' in filename]
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in json_filename]
        data = {}
        for i in range(len(files)):
            data[Path(json_filename[i]).stem] = json.load(files[i])
    return data


def build_db(db_json_path, api_map, setting, value_mapping, mongodb_host=""):
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


def build_user_event(turn, setting, value_mapping):
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
                action[i] = value_mapping.zh2en_DOMAIN_MAP.get(action[i], action[i]).lower()
            elif i == 2 and action[i]:
                action[i] = value_mapping.zh2en_SLOT_MAP.get(action[i], action[i]).replace(' ', '_')
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
    event["active_intent"] = [value_mapping.zh2en_DOMAIN_MAP.get(dom, dom).lower() for dom in turn["turn_domain"]]
    event["state"] = defaultdict(dict)
    for ds, v in turn["belief_state"]["inform slot-values"].items():
        d, s = ds.split("-")[0], ds.split("-")[1]
        d = value_mapping.zh2en_DOMAIN_MAP.get(d, d).lower()
        s = value_mapping.zh2en_SLOT_MAP.get(s, s).replace(' ', '_')
        event["state"][d][s] = {"relation": "equal_to", "value": [process_string(v, setting)]}
    event["state"] = dict(event["state"])
    event["Text"] = process_string(turn["user_utterance"], setting)
    if isinstance(event["Text"], list):
        event["Text"] = event["Text"][0]
    return event


def build_wizard_event(turn, setting, value_mapping, mode="normal"):
    assert mode in ["normal", "query"]
    event = {"Agent": "Wizard"}
    turn_domain_en = [value_mapping.zh2en_DOMAIN_MAP.get(d, d).lower() for d in turn['turn_domain']]
    if mode == "query":
        event["Actions"] = "query"
        event["Constraints"] = defaultdict(dict)
        # event["Constraints_raw"] = defaultdict(dict)
        for ds, v in turn["belief_state"]["inform slot-values"].items():
            # only return matched result in the domains of current turn
            d, s = ds.split("-")
            d = value_mapping.zh2en_DOMAIN_MAP.get(d, d).lower()
            s = value_mapping.zh2en_SLOT_MAP.get(s, s).replace(' ', '_')
            if d in turn_domain_en:
                event["Constraints"][d][s] = process_string(v, setting)
        # TODO: handle multiple APIs
        api_domains = []
        for d in event["Constraints"].keys():
            if d in api_domains:
                continue
            api_domains.append(d)
        event["API"] = api_domains
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
                    action[i] = value_mapping.zh2en_DOMAIN_MAP.get(action[i], action[i]).lower()
                elif i == 2 and action[i]:
                    action[i] = value_mapping.zh2en_SLOT_MAP.get(action[i], action[i]).replace(' ', '_')
                elif i == 3 and action[i]:
                    action[i] = process_string(action[i], setting)
                event_action[action_seq[i]] = action[i]
            event_action["relation"] = "equal_to" if event_action["slot"] and event_action["value"] else ""
            actions.append(event_action)
        event["Actions"] = actions

        event["Text"] = process_string(turn["system_utterance"], setting)
        if isinstance(event["Text"], list):
            event["Text"] = event["Text"][0]
    return event


DIALOGUES_WITH_ISSUE = {
    ('attraction_restaurant_hotel_goal_1-40###5116', 2),
    ('movie_tv_goal_2-67_v2###2464', 5),
    ('tv_goal_1-11_v2###9693', 0),
    ('movie_tv_goal_5-16', 1),
    ('attraction_restaurant_hotel_goal_2-21###6094', '*'),
    ('attraction_restaurant_goal_2-7_v2###2179', 4),
    ('attraction_restaurant_goal_2-7_v2###2179', 5),
    ('Hospital_goal_2-32_v2###9505', '*'),
}


def build_kb_event(
    wizard_query_event, db, actions, expected_num_results, setting, dial_id, turn_id, value_mapping, ground_truth_results=None
):
    event = {"Agent": "KnowledgeBase"}
    constraints = wizard_query_event["Constraints"]
    for d in constraints:
        constraints[d] = {k.replace(" ", "_"): v for k, v in constraints[d].items()}
    api_names = wizard_query_event["API"]
    knowledge = call_api(db, api_names, constraints, lang=setting, value_mapping=value_mapping, actions=actions)
    event["TotalItems"] = sum(item.get("available_options", 0) for api, item in knowledge.items())
    for api, item in knowledge.items():
        if item.get("available_options", 0) < expected_num_results and api_names != ['general']:
            if (dial_id, turn_id) in DIALOGUES_WITH_ISSUE or (dial_id, '*') in DIALOGUES_WITH_ISSUE:
                continue
            print(f'API call likely failed for dial_id: {dial_id}, turn_id: {turn_id}')
            if ground_truth_results is not None:
                constraints[api] = {
                    # case insensitive slot name matching for English
                    (k if setting == 'zh' else k.lower()): (v if setting == 'zh' else value_mapping.en2canonical.get(v, v))
                    for k, v in constraints[api].items()
                }
                for db_item in ground_truth_results:
                    if not isinstance(db_item, dict):
                        db_item = json.loads(db_item.replace("'", '"'))
                    db_item = {
                        (k.lower() if setting != 'zh' else value_mapping.zh2en_SLOT_MAP[k]).replace(" ", "_"): process_string(
                            v, setting
                        )
                        for k, v in db_item.items()
                    }
                    try:
                        # compare the constraints and db_results annotation to see why the API call failed
                        diff = set(constraints[api].items()) - set(db_item.items())
                    except Exception as e:
                        if "unhashable type: 'list'" in str(e):
                            if 'key_departments' in list(constraints[api].keys()):
                                if constraints[api]['key_departments'] in db_item['key_departments']:
                                    diff = {}
                                    continue  # key_departments is a list, it's ok to only mention one of the key departments by user.
                                else:
                                    diff = {'key_departments': constraints[api]['key_departments']}
                            else:
                                hashable_db_item = {k: str(v) for k, v in db_item.items()}
                                diff = set(constraints[api].items()) - set(hashable_db_item.items())
                    if diff:
                        original = {k: db_item[k] if k in db_item else None for k in dict(diff).keys()}
                        if list(original.keys()) == ['number_of_seats'] and int(dict(diff)['number_of_seats']) <= int(
                            original['number_of_seats']
                        ):
                            continue  # number_of_seats doesn't need to be exactly matched
                        else:
                            # print the difference between constraints and db_results for further data correction
                            print('API call likely failed with canonical constraints: {}'.format(constraints))
                            print('difference: {}'.format(diff))
                            print('original: {}'.format(original))
                print(
                    'constraints: {}, available options: {}, expected: {}'.format(
                        constraints[api], item.get("available_options", 0), expected_num_results
                    )
                )
            knowledge = call_api(db, api_names, constraints, lang='zh', value_mapping=value_mapping, actions=actions)

    event["Item"] = knowledge
    event["Topic"] = api_names
    return event


def build_dataset(original_data_path, db, setting, value_mapping, debug=False, mongodb_host=None):
    global dataset

    with open(original_data_path) as fin:
        data = json.load(fin)
    processed_data = {}
    for dialogue in tqdm(data):
        dialogue_id = dialogue["dialogue_id"]
        scenario = {
            "UserTask": dialogue.get("goal", ""),
            "WizardCapabilities": [
                {"Task": value_mapping.zh2en_DOMAIN_MAP.get(domain, domain).lower()} for domain in dialogue["domains"]
            ],
        }
        events = []
        turn_id = 0
        for turn in dialogue["dialogue"]:
            user_turn_event = build_user_event(turn, setting, value_mapping)
            if "db_results" in turn and turn["db_results"]:
                wizard_query_event = build_wizard_event(turn, setting, value_mapping, mode="query")
                wizard_normal_event = build_wizard_event(turn, setting, value_mapping, mode="normal")

                actions = defaultdict(defaultdict)
                for act in wizard_normal_event['Actions']:
                    domain, slot, value = act['domain'], act['slot'], act['value']
                    if slot:
                        actions[domain][slot] = value
                if setting == 'zh':
                    expected_num_results = int(turn["db_results"][0][len('数据库检索结果：成功匹配个数为') :])
                else:
                    expected_num_results = int(turn["db_results"][0].split(" ")[-1])

                if debug:
                    kb_event = build_kb_event(
                        wizard_query_event,
                        db,
                        actions,
                        expected_num_results,
                        setting,
                        dialogue_id,
                        turn_id,
                        value_mapping,
                        ground_truth_results=turn["db_results"][1:],
                    )
                else:
                    kb_event = build_kb_event(
                        wizard_query_event,
                        db,
                        actions,
                        expected_num_results,
                        setting,
                        dialogue_id,
                        turn_id,
                        value_mapping,
                        ground_truth_results=None,
                    )
                user_turn_event['turn_id'] = wizard_query_event['turn_id'] = wizard_normal_event['turn_id'] = turn_id
                events += [user_turn_event, wizard_query_event, kb_event, wizard_normal_event]
            else:
                wizard_event = build_wizard_event(turn, setting, value_mapping)
                user_turn_event['turn_id'] = wizard_event['turn_id'] = turn_id
                events += [user_turn_event, wizard_event]

            turn_id += 1
        processed_data[dialogue_id] = {"Dialogue_id": dialogue_id, "Scenario": scenario, "Events": events}
    return processed_data


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--root", type=str, default='dialogues/risawoz/', help='code root directory')
    parser.add_argument("--data_dir", type=str, default="data/original/", help="path to original data, relative to root dir")
    parser.add_argument("--save_dir", type=str, default="data/", help="path to save preprocessed data, relative to root dir")
    parser.add_argument("--src", type=str, help="en, zh, en_zh", default="zh")
    parser.add_argument("--tgt", type=str, help="en, fr", default="en")
    parser.add_argument("--setting", type=str, help="en, fr, zh, en_zh")
    parser.add_argument("--splits", nargs='+', default=['train', 'valid', 'test'])
    parser.add_argument("--debug", action="store_true", help="toggle debug mode")
    args = parser.parse_args()

    mongodb_host = "mongodb://localhost:27017/"
    dataset = Risawoz(name='risawoz', src=args.src, tgt=args.tgt, mongodb_host=mongodb_host)

    risawoz_db = build_db(
        db_json_path=os.path.join(*[args.root, f'database/db_{args.setting}']),
        api_map=None,
        setting=args.setting,
        value_mapping=dataset.value_mapping,
        mongodb_host=mongodb_host,
    )
    db_client = pymongo.MongoClient(mongodb_host)

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
            os.path.join(original_data_path, f"{args.setting}_{split}.json"),
            risawoz_db,
            args.setting,
            dataset.value_mapping,
            debug=args.debug,
            mongodb_host=mongodb_host,
        )
        # save converted files in JSON format
        with open(f"{processed_data_path}/{args.setting}_{split}.json", 'w') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
