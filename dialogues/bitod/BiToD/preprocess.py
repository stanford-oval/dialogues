import argparse
import json
import os
import random
from collections import OrderedDict, defaultdict

# Mapping between intents, slots, and relations in English and Chinese
from ..BiToD.knowledgebase.en_zh_mappings import *  # noqa
from ..BiToD.utils import action2span, clean_text, compute_lev_span, create_mixed_lang_text, knowledge2span, state2span


def translate_slots_to_english(text):
    for key, val in translation_dict.items():
        text = text.replace(key, val)
    for key, val in zh_API_MAP.items():
        text = text.replace(key, val)
    for key, val in zh2en_CARDINAL_MAP.items():
        text = text.replace(f'" {key} "', f'" {val} "')
    return text


def read_data(args, path_names, setting, max_history=3):
    print(("Reading all files from {}".format(path_names)))
    data = []

    # read files
    for path_name in path_names:
        with open(path_name) as f:
            dials = json.load(f)
            # cross lingual adaptation setting
            # use only 10% data from target lang
            if args.setting in ['en2zh', 'zh2en']:
                _, target_lang = args.setting.split("2")
                if f"{target_lang}_train" in path_name:
                    if not os.path.exists(f"data/{target_lang}_fewshot_dials_{args.fewshot_percent}.json"):
                        dial_ids = list(dials.keys())
                        dial_ids = dial_ids[: int(len(dial_ids) * args.fewshot_percent // 100)]
                        print(f"few shot for {target_lang}, dialogue number: {len(dial_ids)}")
                        with open(f"data/{target_lang}_fewshot_dials_{args.fewshot_percent}.json", "w") as f:
                            json.dump({"fewshot_dials": dial_ids}, f, indent=True)
                    else:
                        with open(f"data/{target_lang}_fewshot_dials_{args.fewshot_percent}.json") as f:
                            dial_ids = json.load(f)["fewshot_dials"]
                    dials = {dial_id: dials[dial_id] for dial_id in dial_ids}

            for dial_id, dial in dials.items():
                dialogue_turns = dial["Events"]

                dialog_history = []
                knowledge = defaultdict(dict)
                last_knowledge_text = "null"
                last_dialogue_state = {}
                count = 1

                intents = []

                turn_id = 0
                while turn_id < len(dialogue_turns):
                    turn = dialogue_turns[turn_id]

                    if turn["Agent"] == "User":
                        if args.gen_full_state or args.simpletod:
                            if API_MAP[turn["active_intent"]] not in intents:
                                intents.append(API_MAP[turn["active_intent"]])
                        else:
                            intents = [API_MAP[turn["active_intent"]]]

                        active_intent = intents[-1]

                        # accumulate dialogue utterances
                        if args.use_user_acts:
                            action_text = action2span(turn["Actions"], active_intent, setting)
                            action_text = clean_text(action_text, is_formal=True)
                            action_text = translate_slots_to_english(action_text)
                            dialog_history.append("USER_ACTS: " + action_text)
                        else:
                            dialog_history.append("USER: " + clean_text(turn["Text"]))

                        if args.last_two_agent_turns and len(dialog_history) >= 4:
                            dial_hist = [dialog_history[-4].replace('AGENT_ACTS:', 'AGENT_ACTS_PREV:')] + dialog_history[-2:]
                        else:
                            dial_hist = dialog_history[-max_history:]

                        dialog_history_text = " ".join(dial_hist)

                        # convert dict of slot-values into text
                        state_text = state2span(last_dialogue_state, required_slots)

                        current_state = {API_MAP[k]: v for k, v in turn["state"].items()}
                        current_state = OrderedDict(sorted(current_state.items(), key=lambda s: s[0]))
                        current_state = {
                            k: OrderedDict(sorted(v.items(), key=lambda s: s[0])) for k, v in current_state.items()
                        }

                        if args.gen_lev_span:
                            # compute the diff between old state and new state
                            intent = intents[0]
                            target = compute_lev_span(last_dialogue_state, current_state, intent)
                        elif args.gen_full_state or args.simpletod:
                            targets = []
                            for intent in intents:
                                targets.append(compute_lev_span({}, current_state, intent))
                            target = ' '.join(targets)
                        else:
                            intent = intents[0]
                            target = compute_lev_span({}, current_state, intent)

                        # update last dialogue state
                        last_dialogue_state = current_state

                        if args.add_end_tokens or args.simpletod:
                            if args.simpletod:
                                input_text = " ".join(
                                    [
                                        "DST:",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )
                            elif not args.no_state:
                                input_text = " ".join(
                                    [
                                        "DST:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<endofstate>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )
                            else:
                                input_text = " ".join(
                                    [
                                        "DST:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )

                        else:
                            if not args.no_state:
                                input_text = " ".join(
                                    [
                                        "DST:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<history>",
                                        dialog_history_text,
                                    ]
                                )
                            else:
                                input_text = " ".join(
                                    [
                                        "DST:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<history>",
                                        dialog_history_text,
                                    ]
                                )

                        # for cross lingual transfer task; not important ;)
                        input_text, target = create_mixed_lang_text(input_text, target, args.pretraining_prefix)

                        dst_data_detail = {
                            "dial_id": dial_id,
                            "task": translate_slots_to_english(active_intent),
                            "turn_id": count,
                            "dialog_history": dialog_history_text,
                            "input_text": input_text,
                            "output_text": translate_slots_to_english(target),
                            "train_target": "dst",
                        }

                        if not args.nlg:
                            data.append(dst_data_detail)

                        turn_id += 1

                    elif turn["Agent"] == "Wizard":
                        # convert dict of slot-values into text
                        state_text = state2span(last_dialogue_state, required_slots)

                        if args.add_end_tokens or args.simpletod:
                            if args.simpletod:
                                input_text = " ".join(
                                    [
                                        "API:",
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<endofstate>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )
                            elif not args.no_state:
                                input_text = " ".join(
                                    [
                                        "API:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<endofstate>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )
                            else:
                                input_text = " ".join(
                                    [
                                        "API:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )

                        else:
                            if not args.no_state:
                                input_text = " ".join(
                                    [
                                        "API:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<history>",
                                        dialog_history_text,
                                    ]
                                )
                            else:
                                input_text = " ".join(
                                    [
                                        "API:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<history>",
                                        dialog_history_text,
                                    ]
                                )

                        if turn["Actions"] == "query":
                            # do api call
                            # next turn is KnowledgeBase
                            assert dialogue_turns[turn_id + 1]["Agent"] == 'KnowledgeBase'
                            next_turn = dialogue_turns[turn_id + 1]
                            # domain = next_turn["Topic"].split("_")[0]

                            if int(next_turn["TotalItems"]) == 0:
                                last_knowledge_text = f"( {active_intent} ) Message = No item available."
                            else:
                                # they only return 1 item
                                knowledge[active_intent].update(next_turn["Item"])
                                last_knowledge_text = knowledge2span(knowledge)

                            api_data_detail = {
                                "dial_id": dial_id,
                                "task": translate_slots_to_english(active_intent),
                                "turn_id": count,
                                "dialog_history": dialog_history_text,
                                "input_text": input_text,
                                "output_text": "yes",
                                "train_target": "api",
                            }

                            if not args.nlg:
                                data.append(api_data_detail)

                            # skip knowledge turn since we already processed it
                            turn_id += 2
                            turn = dialogue_turns[turn_id]

                        else:

                            # no api call
                            api_data_detail = {
                                "dial_id": dial_id,
                                "task": translate_slots_to_english(active_intent),
                                "turn_id": count,
                                "dialog_history": dialog_history_text,
                                "input_text": input_text,
                                "output_text": "no",
                                "train_target": "api",
                            }

                            if not args.nlg:
                                data.append(api_data_detail)

                        # once last_knowledge_text is used reset it
                        # input_text = " ".join(["Response:", "<knowledge>", last_knowledge_text, "<state>", state_text, "<history>", dialog_history_text])
                        if args.add_end_tokens or args.simpletod:
                            if not args.no_state or args.simpletod:
                                input_text = " ".join(
                                    [
                                        "ACTS:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<endofstate>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )
                            else:
                                input_text = " ".join(
                                    [
                                        "ACTS:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<endofknowledge>",
                                        "<history>",
                                        dialog_history_text,
                                        "<endofhistory>",
                                    ]
                                )
                        else:
                            if not args.no_state:
                                input_text = " ".join(
                                    [
                                        "ACTS:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<state>",
                                        translate_slots_to_english(state_text),
                                        "<history>",
                                        dialog_history_text,
                                    ]
                                )
                            else:
                                input_text = " ".join(
                                    [
                                        "ACTS:",
                                        "<knowledge>",
                                        translate_slots_to_english(last_knowledge_text),
                                        "<history>",
                                        dialog_history_text,
                                    ]
                                )

                        # for Metro domain we need to carry over api results
                        # it often happens that in first response agent only provides the shortest_path
                        # then user asks about price and journey duration, and agent reuses old api results to respond
                        if not ('HKMTR' in active_intent or args.add_api_results or args.simpletod):
                            last_knowledge_text = "null"
                            knowledge = defaultdict(dict)

                        target = clean_text(turn["Text"])
                        # for cross lingual transfer task; not important ;)
                        input_text, target = create_mixed_lang_text(input_text, target, args.pretraining_prefix)

                        action_text = action2span(turn["Actions"], active_intent, setting)
                        action_text = clean_text(action_text, is_formal=True)
                        action_text = translate_slots_to_english(action_text)

                        if args.use_natural_response or args.only_gen_natural_response:
                            output_text = target
                        else:
                            output_text = action_text

                        if args.four_steps:
                            input_text = input_text.replace('ACTS:', 'DA:')
                            acts_data_detail = {
                                "dial_id": dial_id,
                                "task": active_intent,
                                "turn_id": count,
                                "dialog_history": dialog_history_text,
                                "input_text": input_text,
                                "output_text": action_text,
                                "train_target": "da",
                            }
                            data.append(acts_data_detail)

                            input_text = " ".join(
                                [
                                    "RG:",
                                    "<actions>",
                                    action_text,
                                    "<endofactions>",
                                    "<history>",
                                    dialog_history_text,
                                    "<endofhistory>",
                                ]
                            )

                            # input_text_rg = " ".join(['RG:', "<actions>", action_text, "<endofactions>", input_text.replace('ACTS: ', '')])
                            response_data_detail = {
                                "dial_id": dial_id,
                                "task": active_intent,
                                "turn_id": count,
                                "dialog_history": dialog_history_text,
                                "input_text": input_text,
                                "output_text": target,
                                "train_target": "rg",
                            }
                            data.append(response_data_detail)
                        else:
                            response_data_detail = {
                                "dial_id": dial_id,
                                "task": active_intent,
                                "turn_id": count,
                                "dialog_history": dialog_history_text,
                                "input_text": input_text,
                                "output_text": output_text,
                                "train_target": "response",
                                "response": target,
                            }
                            data.append(response_data_detail)

                        # update dialogue history
                        if args.simpletod:
                            dialog_history.append("AGENT_ACTS: " + target)
                        elif args.only_gen_natural_response:
                            dialog_history.append("AGENT_ACTS: " + action_text)
                        else:
                            dialog_history.append("AGENT_ACTS: " + output_text)

                        turn_id += 1
                        count += 1

    return data


def prepare_data(args, path_train, path_dev, path_test):
    # "en, zh, en&zh, en2zh, zh2en"
    data_train, data_dev, data_test = None, None, None

    if 'eval' in args.splits:
        data_dev = read_data(args, path_dev, args.setting, args.max_history)
    if 'train' in args.splits:
        data_train = read_data(args, path_train, args.setting, args.max_history)
    if 'test' in args.splits:
        data_test = read_data(args, path_test, args.setting,args. max_history)

    if args.setting == "en_zh":
        if data_train:
            random.shuffle(data_train)
        if data_dev:
            random.shuffle(data_dev)
        if data_test:
            random.shuffle(data_test)

    return data_train, data_dev, data_test

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--save_dir", type=str, default="data/preprocessed", help="path to save prerpocessed data for training"
    )
    parser.add_argument("--setting", type=str, default="en", help="en, zh, en_zh, en2zh, zh2en")
    parser.add_argument("--nlg", action='store_true', help="only keep agent side (for nlg)")
    parser.add_argument(
        "--pretraining_prefix", type=str, default="",
        help="for cross lingual pretrainings: [en2zh_trainsfer, zh2en_trainsfer]"
    )
    parser.add_argument("--max_history", type=int, default=2)
    parser.add_argument("--splits", nargs='+', default=['train', 'eval', 'test'])
    parser.add_argument("--version", type=int)
    parser.add_argument("--fewshot_percent", type=int, default="10")
    parser.add_argument("--use_user_acts", action='store_true')
    parser.add_argument("--gen_lev_span", action='store_true')
    parser.add_argument("--add_end_tokens", action='store_true')
    parser.add_argument("--last_two_agent_turns", action='store_true')
    parser.add_argument("--gen_full_state", action='store_true')
    parser.add_argument("--english_slots", action='store_true')
    parser.add_argument("--use_natural_response", action='store_true')
    parser.add_argument("--no_state", action='store_true')
    parser.add_argument("--add_api_results", action='store_true')
    parser.add_argument("--simpletod", action='store_true')
    parser.add_argument("--only_gen_natural_response", action='store_true')
    parser.add_argument("--four_steps", action='store_true')
    
    args = parser.parse_args()
    
    if not args.english_slots:
        translation_dict = {}

    if args.setting in ["en", "zh2en"]:
        path_train = ["data/en_train.json"]
        path_dev = ["data/en_valid.json"]
        path_test = ["data/en_test.json"]
    elif args.setting in ["zh", "en2zh"]:
        path_train = ["data/zh_train.json"]
        path_dev = ["data/zh_valid.json"]
        path_test = ["data/zh_test.json"]
    else:
        path_train = ["data/zh_train.json", "data/en_train.json"]
        path_dev = ["data/zh_valid.json", "data/en_valid.json"]
        path_test = ["data/zh_test.json", "data/en_test.json"]


    data_train, data_dev, data_test = prepare_data(args, path_train, path_dev, path_test)
    
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
    
    with open(
            os.path.join(
                args.save_dir,
                f"{args.pretraining_prefix}{args.setting}_train" + (
                "_nlg" if args.nlg else "") + f"_v{args.version}.json",
            ),
            "w",
    ) as f:
        json.dump({"version": args.version, "data": data_train}, f, indent=True, ensure_ascii=False)
    
    with open(
            os.path.join(
                args.save_dir,
                f"{args.pretraining_prefix}{args.setting}_valid" + (
                "_nlg" if args.nlg else "") + f"_v{args.version}.json",
            ),
            "w",
    ) as f:
        json.dump({"version": args.version, "data": data_dev}, f, indent=True, ensure_ascii=False)
    
    with open(
            os.path.join(
                args.save_dir,
                f"{args.pretraining_prefix}{args.setting}_test" + (
                "_nlg" if args.nlg else "") + f"_v{args.version}.json",
            ),
            "w",
    ) as f:
        json.dump({"version": args.version, "data": data_test}, f, indent=True, ensure_ascii=False)
        
        with open(os.path.join(f"./data_samples/v{args.version}.json"), "w") as f:
            json.dump({"data": data_test[:30]}, f, indent=True, ensure_ascii=False)


if __name__ == "__main__":
    main()
