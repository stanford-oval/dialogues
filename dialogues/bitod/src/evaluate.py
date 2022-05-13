import argparse
import copy
import json
import os
import re
from collections import OrderedDict, defaultdict

import dictdiffer
from datasets import load_metric

from dialogues.bitod.src.knowledgebase.en_zh_mappings import (
    api_names,
    en_API_MAP,
    r_en_API_MAP,
    required_slots,
    translation_dict,
    zh_en_API_MAP,
)
from dialogues.bitod.src.preprocess import translate_slots_to_english
from dialogues.bitod.src.utils import action2span, canonicalize_constraints, convert_to_int, entity_map, span2state, state2span

metric = load_metric("sacrebleu")


def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]

    return preds, labels


def compute_bleu(preds, labels):
    """
    preds = [pred1, pred2,...]
    labels = [label1, label2,...]
    """
    # Some simple post-processing
    preds, labels = postprocess_text(preds, labels)

    bleu = metric.compute(predictions=preds, references=labels)["score"]
    bleu = round(bleu, 4) / 100.0

    return bleu


def compute_success_rate(predictions, references):
    """
    Success:
    The system is able to offer the correct entities (e.g., restaurant name), provide the correct information (e.g., restaurant address),
    and confirm the booking information with the user before booking.

    Api call Accuracy:
    The predicted api call match the annotated api call.
    """

    total_dial = 0
    total_api_call = 0
    success_dial = 0
    correct_api_call = 0
    task_info = {}

    # out_api = open('out_api.tsv', 'w')
    out_success = open('out_success.tsv', 'w')

    for dial_id in references:
        responses = ""
        total_dial += 1

        # api accuracy
        for api_name, constraints in references[dial_id]["API"].items():
            total_api_call += 1
            pred = predictions[dial_id]["API"].get(api_name)

            pred_sets = convert_lists_to_set_api(pred)
            constraints_sets = convert_lists_to_set_api(constraints)

            if pred_sets == constraints_sets:
                correct_api_call += 1
            # else:
            #     out_api.write(
            #         dial_id
            #         + '\t'
            #         + str(pred)
            #         + '\t'
            #         + str(dict(constraints))
            #         + '\t'
            #         + str(list(dictdiffer.diff(constraints, pred)))
            #         + '\n'
            #     )

        # success
        out = ''
        dial_success_flag = True
        for response in predictions[dial_id]["turns"].values():
            responses += response["response"][0] + " "
        responses = clean_value(responses)
        out += responses + '\t'

        for intent in references[dial_id]["tasks"]:
            if intent not in task_info:
                task_info[intent] = {"total": 0, "hit": 0, "success_rate": 0}
            task_success_flag = True
            task_info[intent]["total"] += 1

            for entity in references[dial_id]["tasks"][intent]["inform+offer"]:
                entity = clean_value(entity)
                if str(entity) not in responses:
                    out += str(entity) + ' ; '
                    task_success_flag = False
                    break
            for entity in references[dial_id]["tasks"][intent]["confirmation"]:
                entity = clean_value(entity)
                if str(entity) not in responses:
                    out += str(entity) + ' ; '
                    task_success_flag = False
                    break
            if task_success_flag:
                task_info[intent]["hit"] += 1
            else:
                dial_success_flag = False

        if dial_success_flag:
            success_dial += 1

        out_success.write(out + '\n')

    total_tasks = 0
    success_tasks = 0
    for task in task_info:
        task_info[task]["success_rate"] = task_info[task]["hit"] / task_info[task]["total"]
        total_tasks += task_info[task]["total"]
        success_tasks += task_info[task]["hit"]
    task_info["Averaged_task_success"] = success_tasks / total_tasks
    success_rate = success_dial / total_dial
    api_acc = correct_api_call / total_api_call
    return success_rate, api_acc, task_info


def clean_value(v, do_int=False):
    # return v
    v = str(v)
    v = v.lower()

    v = v.replace("，", ",")
    v = v.replace('..', '.')

    if re.search('(\d+)[\.:](\d+)\s?(afternoon|in the afternoon)', v):
        v = re.sub('(\d+)[\.:](\d+)\s?(?:pm )?(afternoon|in the afternoon)', r'\1:\2 pm', v)
    if re.search('(\d+)[\.:](\d+)\s?(?:am )?(morning|in the morning)', v):
        v = re.sub('(\d+)[\.:](\d+)\s?(morning|in the morning)', r'\1:\2 am', v)
    if re.search('(\d+)[\.:](\d+)\s?(am|pm)', v):
        v = re.sub('(\d+)[\.:](\d+)\s?(am|pm)', r'\1:\2 \3', v)
    if re.search(' [\&\/] ', v):
        v = re.sub(' [\&\/] ', ' and ', v)
        v = re.sub('\s+', ' ', v)
    if re.search(' ([\w\d]+)\.(?:\s|$)', v):
        v = re.sub(' ([\w\d]+)\.(?:\s|$)', r' \1 ', v)

    # time consuming but needed step
    for key, val in entity_map.items():
        key, val = str(key), str(val)
        if key in v:
            v = v.replace(key, val)
    # v = entity_map.get(v, v)

    if do_int:
        v = convert_to_int(v, word2number=True)

    v = str(v)
    return v


def convert_lists_to_set(state):
    new_state = copy.deepcopy(state)
    for i in state:
        for j in state[i]:
            for m, v in state[i][j].items():
                if isinstance(v, list):
                    v = [clean_value(val, do_int=True) for val in v]
                    new_state[i][j][m] = set(v)
                else:
                    v = clean_value(v, do_int=True)
                    new_state[i][j][m] = v
    return new_state


def convert_lists_to_set_api(constraints):
    new_constraints = copy.deepcopy(constraints)
    if constraints:
        for k, v in constraints.items():
            if isinstance(v, dict):
                for i, j in v.items():
                    if isinstance(j, list):
                        j = [clean_value(val, do_int=True) for val in j]
                        new_constraints[k][i] = set(j)
            elif isinstance(v, str):
                v = clean_value(v, do_int=True)
                new_constraints[k] = v
    return new_constraints


out_dst = open('out_dst.tsv', 'w')


def compute_result(args, predictions, reference_data):
    task_info = {}
    bleu, ser, success_rate, api_acc, da_acc, JGA = 0, 0, 0, 0, 0, 0

    if args.eval_task in ["dst", "end2end"]:
        hit = 0
        total_dst_turns = 0
        for dial_id in reference_data:
            pred_turn_id = 0
            for turn in reference_data[dial_id]["Events"]:
                if turn["Agent"] == "User":
                    pred_turn_id += 1
                    total_dst_turns += 1

                    pred = predictions[dial_id]["turns"][str(pred_turn_id)]["state"]
                    gold = turn["state"]

                    if args.setting == 'zh':
                        gold = state2span(gold, required_slots)
                        gold = translate_slots_to_english(gold)
                        gold = span2state(gold, api_names)
                        gold = {r_en_API_MAP.get(k, k): v for k, v in gold.items()}

                    pred_sets = convert_lists_to_set(pred)
                    gold_sets = convert_lists_to_set(gold)

                    if pred_sets == gold_sets:
                        hit += 1
                    else:
                        out_dst.write(
                            dial_id
                            + '/'
                            + str(pred_turn_id)
                            + '\t'
                            + str(pred)
                            + '\t'
                            + str(gold)
                            + '\t'
                            + str(list(dictdiffer.diff(gold, pred)))
                            + '\n'
                        )

        JGA = hit / total_dst_turns

    if args.eval_task in ["end2end", "response"]:
        reference_task_success = defaultdict(dict)
        reference_act_values = []
        reference_actions = []
        reference_response = []
        predicted_response = []
        predicted_actions = []
        for dial_id in reference_data:
            if dial_id not in reference_task_success:
                reference_task_success[dial_id]["tasks"] = {
                    zh_en_API_MAP.get(task["Task"], task["Task"]): {"inform+offer": [], "confirmation": []}
                    for task in reference_data[dial_id]["Scenario"]["WizardCapabilities"]
                }
                reference_task_success[dial_id]["API"] = {}
            pred_turn_id = 1
            user_requested_info = defaultdict(dict)
            confirm_info = defaultdict(dict)
            for turn in reference_data[dial_id]["Events"]:
                if turn["Agent"] == "User":
                    intent = turn["active_intent"]
                    intent = zh_en_API_MAP.get(intent, intent)
                if turn["Agent"] == "Wizard":
                    if turn["Actions"] == "query":
                        constraints = canonicalize_constraints(turn["Constraints"])
                        turn_api = zh_en_API_MAP.get(turn["API"], turn["API"])
                        if args.setting == 'zh' and constraints:
                            constraints = {translation_dict[k]: v for k, v in constraints.items()}
                        reference_task_success[dial_id]["API"][turn_api] = constraints
                    else:
                        reference_response.append(clean_value(turn["Text"]))
                        act_values = set()
                        for item in turn["Actions"]:
                            if len(item["value"]):
                                act_values.update(item["value"])
                            act_values = set([clean_value(val) for val in act_values])
                        reference_act_values.append(act_values)

                        reference_actions.append(clean_value(action2span(turn["Actions"], en_API_MAP[intent], 'en')))

                        predicted_response.append(clean_value(predictions[dial_id]["turns"][str(pred_turn_id)]["response"][0]))
                        predicted_actions.append(clean_value(predictions[dial_id]["turns"][str(pred_turn_id)]["actions"]))

                        pred_turn_id += 1

                        # For each task, the last value for each slot are considered as final requested information from user
                        for action in turn["Actions"]:
                            trans_slot = action["slot"]
                            if args.setting == 'zh' and action["slot"]:
                                if action["slot"] == 'start_date':
                                    trans_slot = 'start_date'
                                else:
                                    trans_slot = translation_dict[action["slot"]]
                            if (
                                (action["act"] in ["inform", "offer"])
                                and (len(action["value"]) > 0)
                                and action["slot"] != "available_options"
                                and action["slot"] != "可用选项"
                            ):
                                user_requested_info[intent][trans_slot] = action["value"]
                            elif (action["act"] == "confirm") and (len(action["value"]) > 0):
                                confirm_info[intent][trans_slot] = action["value"]
            for intent, slot_values in user_requested_info.items():
                for values in slot_values.values():
                    reference_task_success[dial_id]["tasks"][intent]["inform+offer"] += values
            for intent, slot_values in confirm_info.items():
                for values in slot_values.values():
                    reference_task_success[dial_id]["tasks"][intent]["confirmation"] += values

        bleu = compute_bleu(predicted_response, reference_response)
        ser = compute_ser(predicted_response, reference_act_values)
        da_acc = compute_da(predicted_actions, reference_actions)

        success_rate, api_acc, task_info = compute_success_rate(predictions, reference_task_success)

    if 'Averaged_task_success' in task_info:
        task_info['Averaged_task_success'] *= 100
    return OrderedDict(
        {
            "bleu": bleu * 100,
            "ser": ser * 100,
            "success_rate": success_rate * 100,
            "api_acc": api_acc * 100,
            "da_acc": da_acc * 100,
            "jga": JGA * 100,
            "task_info": task_info,
        }
    )


def compute_da(preds, refs):
    da = 0.0
    for pred, ref in zip(preds, refs):
        if pred:
            if ref == pred:
                da += 1
    return da / len(preds)


def compute_ser(preds, act_values):
    ser = 0.0
    for pred, values in zip(preds, act_values):
        # remove emtpy slot values
        missing = False
        if len(values):
            for val in values:
                if str(val) not in pred:
                    missing = True
        if missing:
            ser += 1.0
    return ser / len(preds)


def eval_file(args, prediction_file_path, reference_file_path):

    reference_data = {}
    for reference_file_path in reference_file_path.split("__"):
        with open(reference_file_path) as f:
            reference_data.update(json.load(f))

    with open(prediction_file_path) as f:
        predictions = json.load(f)

    if not args.setting:
        file = os.path.basename(reference_file_path)
        if 'zh' in file:
            args.setting = 'zh'
        else:
            args.setting = 'en'

    results = compute_result(args, predictions, reference_data)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference_file_path", type=str, default="data/test.json", help="path of reference")
    parser.add_argument("--prediction_file_path", type=str, help="path of prediction")
    parser.add_argument("--eval_task", type=str, default="end2end", help="end2end, dst, response")
    parser.add_argument("--setting", type=str, default="en", help="en, zh, en&zh, en2zh, zh2en")
    parser.add_argument("--result_path", type=str, default="./", help="eval_model or eval_file?")
    parser.add_argument("--save_prefix", type=str, default="", help="prefix of save file name")

    args = parser.parse_args()

    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)

    results = eval_file(args, args.prediction_file_path, args.reference_file_path)

    with open(os.path.join(args.result_path, f"{args.save_prefix}{args.setting}_{args.eval_task}_result.json"), "w") as f:
        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
