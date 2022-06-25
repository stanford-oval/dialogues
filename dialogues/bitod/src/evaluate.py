import argparse
import copy
import json
import os
import re
from collections import OrderedDict, defaultdict

import dictdiffer
from bitod.src.knowledgebase.en_zh_mappings import BitodMapping
from datasets import load_metric

from dialogues.bitod.src.utils import action2span, canonicalize_constraints, convert_to_int, span2action

metric = load_metric("sacrebleu")


value_mapping = BitodMapping()


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
    bleu = round(bleu, 4)

    return bleu


out_da = open('out_da.tsv', 'w')


def compute_da(preds, refs):
    da = 0.0
    for pred, ref in zip(preds, refs):
        if pred:
            pred = clean_value(pred)
            pred_dict = span2action(pred, value_mapping.api_names)

            ref = clean_value(ref)
            ref_dict = span2action(ref, value_mapping.api_names)

            if pred_dict == ref_dict:
                da += 1
            else:
                out_da.write(str(pred) + '\t' + str(ref) + '\t' + str(list(dictdiffer.diff(pred, ref))) + '\n')

    return da / len(preds) * 100


out_ser = open('out_ser.tsv', 'w')


def compute_ser(preds, act_values):
    ser = 0.0
    for pred, values in zip(preds, act_values):
        # remove emtpy slot values
        missing = False
        if len(values):
            for val in values:
                if val == 'null':
                    continue
                if str(val) not in pred:
                    missing = True
        if missing:
            ser += 1.0
            out_ser.write('\t'.join([pred, *values]) + '\n')
    return ser / len(preds) * 100


out_dst = open('out_dst.tsv', 'w')


def compute_dst_em(preds, golds):
    hit = 0
    for pred, gold in zip(preds, golds):
        pred_sets = convert_lists_to_set(pred)
        gold_sets = convert_lists_to_set(gold)

        if pred_sets == gold_sets:
            hit += 1
        else:
            out_dst.write(
                str(pred_sets) + '\t' + str(gold_sets) + '\t' + str(list(dictdiffer.diff(pred_sets, gold_sets))) + '\n'
            )

    return hit / len(preds) * 100


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

    out_api = open('out_api.tsv', 'w')
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
            else:
                out_api.write(
                    dial_id
                    + '\t'
                    + str(pred_sets)
                    + '\t'
                    + str(constraints_sets)
                    + '\t'
                    + str(list(dictdiffer.diff(pred_sets, constraints_sets)))
                    + '\n'
                )
        api_acc = correct_api_call / total_api_call * 100

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
    task_info["Averaged_task_success"] = success_tasks / total_tasks * 100
    success_rate = success_dial / total_dial * 100
    return success_rate, api_acc, task_info


FAST_EVAL = False


def clean_value(v, do_int=False):
    v = str(v)
    v = v.lower()
    v = v.strip()

    v = v.replace("，", ",")
    v = v.replace('..', '.')

    # am, pm
    v = re.sub('(\d+)(?:[\.:](\d+))?\s?(?:pm )?(afternoon|in the afternoon|pm in the afternoon)', r'\1:\2 pm', v)
    v = re.sub('(\d+)(?:[\.:](\d+))?\s?(morning|in the morning|am in the morning)', r'\1:\2 am', v)
    v = re.sub('(\d+)(?:[\.:](\d+))?\s?(am|pm)', r'\1:\2 \3', v)

    # & --> and
    v = re.sub(' [\&\/] ', ' and ', v)
    v = re.sub('\s+', ' ', v)

    # remove extra dot in the end
    v = re.sub('(\d+)\.$', r'\1', v)
    v = re.sub('(\w+)\.$', r'\1', v)

    # 3rd of january --> januray 3
    v = re.sub('(\d+)(?:th|rd|st|nd) of (\w+)', r'\2 \1', v)

    # time consuming but needed step
    if not FAST_EVAL:
        for key, val in value_mapping.entity_map.items():
            key, val = str(key), str(val)
            if key in v:
                v = v.replace(key, val)

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
                    new_state[i][j][m] = clean_value(v, do_int=True)
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
                    else:
                        new_constraints[k][i] = clean_value(j, do_int=True)
            else:
                new_constraints[k] = clean_value(v, do_int=True)
    return new_constraints


def compute_result(predictions, reference_data):

    preds = []
    golds = []
    for dial_id in reference_data:
        pred_turn_id = 0
        for turn in reference_data[dial_id]["Events"]:
            if turn["Agent"] == "User":
                pred_turn_id += 1

                pred = predictions[dial_id]["turns"][str(pred_turn_id)]["state"]
                gold = turn["state"]

                preds.append(pred)
                golds.append(gold)

    jga = compute_dst_em(preds, golds)

    reference_task_success = defaultdict(dict)
    reference_act_values = []
    reference_actions = []
    reference_response = []
    predicted_response = []
    predicted_actions = []
    for dial_id in reference_data:
        if dial_id not in reference_task_success:
            reference_task_success[dial_id]["tasks"] = {
                value_mapping.zh_en_API_MAP.get(task["Task"], task["Task"]): {"inform+offer": [], "confirmation": []}
                for task in reference_data[dial_id]["Scenario"]["WizardCapabilities"]
            }
            reference_task_success[dial_id]["API"] = {}
        pred_turn_id = 1
        user_requested_info = defaultdict(dict)
        confirm_info = defaultdict(dict)
        for turn in reference_data[dial_id]["Events"]:
            if turn["Agent"] == "User":
                if not isinstance(turn["active_intent"], list):
                    # for compatibility of both BiTOD and RiSAWOZ
                    intent = [value_mapping.zh_en_API_MAP.get(turn["active_intent"], turn["active_intent"])]
                else:
                    intent = turn["active_intent"]
            if turn["Agent"] == "Wizard":
                if turn["Actions"] == "query":
                    if not isinstance(turn["API"], list):
                        # for compatibility of both BiTOD and RiSAWOZ
                        turn["API"] = [turn["API"]]
                        constraints = canonicalize_constraints(turn["Constraints"])
                    else:
                        # TODO: canonicalization for RiSAWOZ
                        constraints = turn["Constraints"]
                    for turn_api in turn["API"]:
                        turn_api = value_mapping.zh_en_API_MAP.get(turn_api, turn_api)
                        if constraints:
                            if turn_api in constraints.keys():
                                # for RiSAWOZ: filter constraints with current API
                                constraints = {k: v for k, v in constraints[turn_api].items()}
                            else:
                                constraints = {k: v for k, v in constraints.items()}
                        reference_task_success[dial_id]["API"][turn_api] = constraints
                else:
                    reference_response.append(clean_value(turn["Text"]))
                    act_values = set()
                    for item in turn["Actions"]:
                        if len(item["value"]):
                            if not isinstance(item["value"], list):
                                item["value"] = [item["value"]]
                            for value in item["value"]:
                                if not isinstance(value, list):
                                    value = [value]
                                act_values.update(value)
                        act_values = set([clean_value(val) for val in act_values])
                    reference_act_values.append(act_values)

                    for i in range(len(intent)):
                        # for RiSAWOZ: filter turn actions with current intent
                        turn_actions = (
                            [action for action in turn["Actions"] if action["domain"] == intent[i]]
                            if len(intent) > 1
                            else turn["Actions"]
                        )
                        reference_actions.append(
                            clean_value(action2span(turn_actions, value_mapping.en_API_MAP.get(intent[i], intent[i]), 'en'))
                        )

                    predicted_response.append(clean_value(predictions[dial_id]["turns"][str(pred_turn_id)]["response"][0]))
                    predicted_actions.append(clean_value(predictions[dial_id]["turns"][str(pred_turn_id)]["actions"]))

                    pred_turn_id += 1

                    # For each task, the last value for each slot are considered as final requested information from user
                    for action in turn["Actions"]:
                        trans_slot = action["slot"]
                        if (
                            (action["act"] in ["inform", "offer"])
                            and (len(action["value"]) > 0)
                            and action["slot"] != "available_options"
                            and action["slot"] != "可用选项"
                        ):
                            for i in range(len(intent)):
                                # for RiSAWOZ: filter turn actions with current intent
                                if len(intent) <= 1 or action["domain"] == intent[i]:
                                    user_requested_info[intent[i]][trans_slot] = action["value"]
                        elif (action["act"] == "confirm") and (len(action["value"]) > 0):
                            # risawoz has no confirm act
                            assert len(intent) == 1
                            confirm_info[intent[0]][trans_slot] = action["value"]
        for intent, slot_values in user_requested_info.items():
            if intent in ["通用"]:  # for RiSAWOZ
                continue
            for values in slot_values.values():
                reference_task_success[dial_id]["tasks"][intent]["inform+offer"] += values
        for intent, slot_values in confirm_info.items():
            if intent in ["通用"]:  # for RiSAWOZ
                continue
            for values in slot_values.values():
                reference_task_success[dial_id]["tasks"][intent]["confirmation"] += values

    bleu = compute_bleu(predicted_response, reference_response)
    ser = compute_ser(predicted_response, reference_act_values)
    da_acc = compute_da(predicted_actions, reference_actions)

    success_rate, api_acc, task_info = compute_success_rate(predictions, reference_task_success)

    return OrderedDict(
        {
            "bleu": bleu,
            "ser": ser,
            "success_rate": success_rate,
            "api_acc": api_acc,
            "da_acc": da_acc,
            "jga": jga,
            "task_info": task_info,
        }
    )


def eval_file(args, prediction_file_path, reference_file_path):
    global FAST_EVAL
    FAST_EVAL = args.fast_eval

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

    results = compute_result(predictions, reference_data)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference_file_path", type=str, default="data/test.json", help="path of reference")
    parser.add_argument("--prediction_file_path", type=str, help="path of prediction")
    parser.add_argument("--setting", type=str, default="en", help="en, zh, en&zh, en2zh, zh2en")
    parser.add_argument("--result_path", type=str, default="./", help="eval_model or eval_file?")
    parser.add_argument("--save_prefix", type=str, default="", help="prefix of save file name")
    parser.add_argument("--fast_eval", action='store_true', help="skip time consuming normalization step")

    args = parser.parse_args()

    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)

    results = eval_file(args, args.prediction_file_path, args.reference_file_path)

    with open(os.path.join(args.result_path, f"{args.save_prefix}{args.setting}_result.json"), "w") as f:
        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
