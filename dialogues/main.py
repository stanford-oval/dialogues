import copy
import json
import os
import random
import re
from collections import OrderedDict, defaultdict

import dictdiffer
from datasets import load_metric
from tqdm import tqdm

from dialogues.utils import (
    clean_text,
    convert_to_int,
    is_at_least,
    is_equal_to,
    is_less_than,
    is_not,
    is_one_of,
    replace_word,
    zh2en_CARDINAL_MAP,
)

metric = load_metric("sacrebleu")


class Dataset(object):
    def __init__(self, name):

        # name of the dataset
        self.name = name

        # value mapping between different languages
        self.value_mapping = None

        # database
        self.db = None

        self.FAST_EVAL = False
        self.DEBUG = True

        # regex to extract belief state span from input
        self.state_re = re.compile('')

        # regex to extract knowledge span (api results) from input
        self.knowledge_re = re.compile('')

        # regex to extract dialogue history from input
        self.history_re = re.compile('')

        # regex to extract agent dialogue acts from input
        self.actions_re = re.compile('')

        self.system_token = ''
        self.user_token = ''

        if self.DEBUG:
            self.out_ser = open('out_ser.tsv', 'w')
            self.out_dst = open('out_dst.tsv', 'w')
            self.out_da = open('out_da.tsv', 'w')

    def domain2api_name(self, domain):
        """
        map domain name to api name used to query the database. these can be the same.
        :param domain: str
        :return: str
        """
        raise NotImplementedError

    def state2span(self, dialogue_state):
        """
        converts dictionary of dialogue state to a text span
        :param dialogue_state: dict
        :return: str
        """
        raise NotImplementedError

    def span2state(self, state_span):
        """
        converts dialogue state text span to a dictionary
        :param state_span: str
        :return: dict
        """
        raise NotImplementedError

    def update_state(self, lev, cur_state):
        """
        Updates cur_state according to the levenshtein state
        :param lev: dict
        :param cur_state: dict
        :return: dict
        """
        raise NotImplementedError

    def process_data(self, args):
        """
        converts raw dataset to the format accepted by genienlp
        each dialogue turn is broken down into 4 subtasks:
        Dialogue State Tracking (DST), API call decision (API) , Dialogue Act generation (DA), Response Generation (RG)
        :param args: dictionary of arguments passed to underlying data processor
        :return: three lists containing dialogues for each data split
        """
        raise NotImplementedError

    def make_api_call(self, dialogue_state, knowledge, api_name, **kwargs):
        """
        given dialogue state and api_name, compute the constraints for api call, make the call, and return the results in text form
        :param dialogue_state: dict
        :param knowledge: dict, keeping track returned api results
        :param api_name: str
        :param kwargs: additional args to pass to api call function
        :return: a dictionary of constraints used as input to api caller
        :return: text version of updated knowledge
        """
        raise NotImplementedError

    def compute_metrics(self, args, prediction_path, reference_path):
        """
        compare predictions vs gold and compute metrics. prediction file should contain model predictions for each subtask for each turn.
        reference file can be the original raw data file or a preprocessed version if it contains all needed info to calculate the required metrics
        :param args: dictionary of arguments passed to underlying evaluation code
        :param prediction_path: path to file containing model predictions
        :param reference_path: path to file containing gold values to compare predictions against
        :return: a dictionary with metric names as keys and their computed values (in percentage)
        """
        raise NotImplementedError

    def postprocess_prediction(self, prediction, **kwargs):
        """
        rule-based postprocessings done on model predictions
        :param prediction: str
        :param kwargs: additional args used for postprocessing
        :return: modified prediction
        """
        pass


class WOZDataset(Dataset):
    # Datasets annotated with slot-relation-values (does not have to be collected WOZ style)
    def __init__(self, name='woz'):
        super().__init__(name)

        # name of the dataset
        self.name = name

        # value mapping between different languages
        self.value_mapping = None

        self.db = None

        self.FAST_EVAL = False

        # regex to extract belief state span from input
        self.state_re = re.compile('<state> (.*?) <endofstate>')

        # regex to extract knowledge span (api results) from input
        self.knowledge_re = re.compile('<knowledge> (.*?) <endofknowledge>')

        # regex to extract dialogue history from input
        self.history_re = re.compile('<history> (.*?) <endofhistory>')

        # regex to extract agent dialogue acts from input
        self.actions_re = re.compile('<actions> (.*?) <endofactions>')

        # regex to user input from history
        self.user_re = re.compile('(?:USER|USER_ACTS): (.*?)(?:$|<)')

        # regex to system input from history
        self.system_re = re.compile('AGENT_ACTS: (.*?)(?:$|<)')

        self.system_token = 'AGENT_ACTS:'
        self.user_token = 'USER:'

    def domain2api_name(self, domain):
        """
        map domain name to api name used to query the database. these can be the same.
        :param domain: str
        :return: str
        """
        return domain

    def process_data(self, args):
        """
        converts raw dataset to the format accepted by genienlp
        each dialogue turn is broken down into 4 subtasks:
        Dialogue State Tracking (DST), API call decision (API) , Dialogue Act generation (DA), Response Generation (RG)
        :param args: dictionary of arguments passed to underlying data processor
        :return: three lists containing dialogues for each data split
        """
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

        path_train = [os.path.join(args.root, p) for p in path_train]
        path_dev = [os.path.join(args.root, p) for p in path_dev]
        path_test = [os.path.join(args.root, p) for p in path_test]

        train, fewshot, dev, test = self.prepare_data(args, path_train, path_dev, path_test)
        return train, fewshot, dev, test

    def postprocess_prediction(self, prediction, **kwargs):
        """
        rule-based postprocessings done on model predictions
        :param prediction: str
        :param kwargs: additional args used for postprocessing
        :return: modified prediction
        """
        return prediction

    def update_state(self, lev, cur_state):
        """
        Updates cur_state according to the levenshtein state
        :param lev: dict
        :param cur_state: dict
        :return: dict
        """
        for api_name in lev:
            if api_name not in cur_state:
                cur_state[api_name] = lev[api_name]
            else:
                cur_state[api_name].update(lev[api_name])

    def compute_metrics(self, args, prediction_path, reference_path):
        """
        compare predictions vs gold and compute metrics. prediction file should contain model predictions for each subtask for each turn.
        reference file can be the original raw data file or a preprocessed version if it contains all needed info to calculate the required metrics
        :param args: dictionary of arguments passed to underlying evaluation code
        :param prediction_path: path to file containing model predictions
        :param reference_path: path to file containing gold values to compare predictions against
        :return: a dictionary with metric names as keys and their computed values (in percentage)
        """

        reference_data = {}
        for reference_file_path in reference_path.split("__"):
            with open(reference_file_path) as f:
                reference_data.update(json.load(f))

        with open(prediction_path) as f:
            predictions = json.load(f)

        if not args.setting:
            file = os.path.basename(reference_path)
            if 'zh' in file:
                args.setting = 'zh'
            else:
                args.setting = 'en'

        results = self.compute_result(predictions, reference_data)

        return results

    def construct_input(
        self,
        train_target,
        state=None,
        user_history=None,
        system_history=None,
        knowledge=None,
        actions=None,
        last_two_agent_turns=True,
        only_user_rg=True,
    ):
        if last_two_agent_turns and len(system_history) >= 2:
            history = [system_history[-2].replace('AGENT_ACTS:', 'AGENT_ACTS_PREV:'), system_history[-1], user_history[-1]]
        elif len(system_history) and len(user_history):
            history = [system_history[-1], user_history[-1]]
        elif len(user_history):
            history = [user_history[-1]]
        else:
            history = []

        history_text = " ".join(history)

        if train_target == 'dst':
            input_text = " ".join(
                [
                    "DST:",
                    "<state>",
                    state,
                    "<endofstate>",
                    "<history>",
                    history_text,
                    "<endofhistory>",
                ]
            )
        elif train_target == 'api':
            input_text = " ".join(
                [
                    "API:",
                    "<knowledge>",
                    knowledge,
                    "<endofknowledge>",
                    "<state>",
                    state,
                    "<endofstate>",
                    "<history>",
                    history_text,
                    "<endofhistory>",
                ]
            )
        elif train_target == 'da':
            input_text = " ".join(
                [
                    "DA:",
                    "<knowledge>",
                    knowledge,
                    "<endofknowledge>",
                    "<state>",
                    state,
                    "<endofstate>",
                    "<history>",
                    history_text,
                    "<endofhistory>",
                ]
            )

        elif train_target == 'rg':
            if only_user_rg:
                history_text = user_history[-1]

            input_text = " ".join(
                [
                    "RG:",
                    "<actions>",
                    actions,
                    "<endofactions>",
                    "<history>",
                    history_text,
                    "<endofhistory>",
                ]
            )

        return input_text

    def span2state(self, state_span):
        """
        converts dialogue state text span to a dictionary
        :param state_span: str
        :return: dict
        """
        # reverse direction of state2span function
        # converts text span to state dict

        state = defaultdict(dict)
        re_intent_spans = re.compile('\( (.*?) \)\s?(.*?)(?=$|\( )')
        re_srvs = re.compile('(\S*? \S*? " .*? "|\S*? #unknown)')

        matches = re_intent_spans.findall(state_span)

        for match in matches:
            intent, srv_span = match
            state[intent] = {}
            if intent in self.value_mapping.api_names:
                srv_matches = re_srvs.findall(srv_span)
                for srv in srv_matches:
                    if '#unknown' in srv:
                        continue
                    else:
                        try:
                            slot, relation, value = srv.split(' ', 2)
                        except Exception:
                            print(f'illegal syntax for slot-relation-values: {srv}')
                            continue

                    # remove " "
                    value = value[2:-2]
                    values = value.split(' | ')
                    values = [convert_to_int(val) for val in values]
                    state[intent][slot] = {"relation": relation, "value": values}

        return state

    def state2constraints(self, dict_data):
        # converts dialogue state to constraints canonical form
        constraints = {}
        for slot, r_v in dict_data.items():
            if r_v["value"] == ["don't care"] or r_v["value"] == ["不在乎"]:
                continue
            relation = r_v["relation"]
            values = r_v["value"]
            if relation != "one_of" and relation != self.value_mapping.en2zh_RELATION_MAP["one_of"]:
                values = values[0]
                if slot in [
                    'stars',
                    'rating',
                    'max_temp',
                    'min_temp',
                    'price_per_night',
                    'number_of_rooms',
                    'number_of_people',
                    'num_of_rooms',
                    'start_day',
                    'start_month',
                    'number_of_nights',
                ]:
                    values = convert_to_int(values, strict=False, word2number=True)
            if relation == "one_of" or relation == self.value_mapping.en2zh_RELATION_MAP["one_of"]:
                constraints[slot] = is_one_of(values)
            elif relation == "at_least" or relation == self.value_mapping.en2zh_RELATION_MAP["at_least"]:
                constraints[slot] = is_at_least(values)
            elif relation == "not" or relation == self.value_mapping.en2zh_RELATION_MAP["not"]:
                constraints[slot] = is_not(values)
            elif relation == "less_than" or relation == self.value_mapping.en2zh_RELATION_MAP["less_than"]:
                constraints[slot] = is_less_than(values)
            else:
                constraints[slot] = is_equal_to(values)
        return constraints

    def canonicalize_constraints(self, dict_data):
        # converts the constraints dictionary in the original data to canonical form
        constraints = {}
        for const in dict_data:
            for slot, values in const.items():
                relation = values[values.find(".") + 1 : values.find("(")]
                values = values[values.find("(") + 1 : -1]
                values = self.value_mapping.entity_map.get(values, values)

                if relation == "one_of" or relation == self.value_mapping.en2zh_RELATION_MAP["one_of"]:
                    values = values.split(" , ")
                else:
                    values = convert_to_int(values, word2number=True)
                if relation == "one_of" or relation == self.value_mapping.en2zh_RELATION_MAP["one_of"]:
                    constraints[slot] = is_one_of(values)
                elif relation == "at_least" or relation == self.value_mapping.en2zh_RELATION_MAP["at_least"]:
                    constraints[slot] = is_at_least(values)
                elif relation == "not" or relation == self.value_mapping.en2zh_RELATION_MAP["not"]:
                    constraints[slot] = is_not(values)
                elif relation == "less_than" or relation == self.value_mapping.en2zh_RELATION_MAP["less_than"]:
                    constraints[slot] = is_less_than(values)
                else:
                    constraints[slot] = is_equal_to(values)
        constraints = OrderedDict(sorted(constraints.items()))
        if constraints == {}:
            constraints = None
        return constraints

    def span2action(self, api_span):
        # reverse direction of state2span fuction
        # converts text span to state dict

        action = defaultdict(list)
        re_intent_spans = re.compile('\( (.+?) \) (.+?)(?=$|, \( )')
        re_asrs = re.compile('((?:\S+? ){3}" .+? "|\S*? \S+?(?: ,|$)|\S+?(?: ,|$))')

        matches = re_intent_spans.findall(api_span)

        for match in matches:
            intent, srv_span = match
            if intent in self.value_mapping.api_names:
                asr_matches = re_asrs.findall(srv_span)
                for asr in asr_matches:
                    slot, value, relation = 'null', 'null', 'null'
                    asr = asr.strip(' ,')
                    if '"' not in asr:
                        parts = asr.split(' ')
                        if len(parts) == 1:
                            act = parts[0]
                        else:
                            assert len(parts) == 2
                            act, slot = parts
                    else:
                        try:
                            act, slot, relation, value = asr.split(' ', 3)
                        except:
                            print(f'api_span: {api_span}, asr: {asr}')
                            continue

                    if value != 'null':
                        # remove " "
                        value = value[2:-2]
                        values = value.split(' | ')
                        values = [convert_to_int(val) for val in values]
                    else:
                        values = ['null']

                    action[intent].append({"act": act, "slot": slot, "relation": relation, "value": values})

        return action

    def action2span_for_single_intent(self, agent_actions, intent, setting):
        action_text = f'( {intent} ) '

        # sort based on act, then slot
        agent_actions = list(sorted(agent_actions, key=lambda s: (s['act'], s['slot'])))

        for action in agent_actions:
            act, slot, relation, values = action['act'], action['slot'], action['relation'], action['value']
            act = act.lower()

            if not act:
                # TODO: there are few annotation errors for act in RiSAWOZ, which makes "act" field empty
                #       this may cause unknown problems
                #       I'll fix it later. Current solution is just a workaround.
                continue
            orig_act = act
            if setting == 'zh':
                if act not in self.value_mapping.en2zh_ACT_MAP:
                    print(f'Encountered illegal act: {act}')
                    continue
                act = self.value_mapping.en2zh_ACT_MAP[act]

            values = [val for val in values if val != ""]
            if len(values):
                values = ' | '.join(map(str, values))
            else:
                values = 'null'

            if orig_act in [
                'notify_success',
                'notify_fail',
                'affirm',
                'request_more',
                'goodbye',
                'greeting',
                'thank_you',
                'negate',
                # for RiSAWOZ
                'bye',
                'general',
            ]:
                action_text += f'{act} , '
            # for RiSAWOZ
            elif orig_act in ['inform', 'recommend']:
                # TODO: annotation error; missing slot
                if not slot or values == 'null':
                    continue
                action_text += f'{act} {slot} {relation} " {values} " , '
            elif orig_act in ['request', 'request_update']:
                action_text += f'{act} {slot} , '
            # for RiSAWOZ
            elif orig_act in ['no-offer']:
                if not slot:
                    slot = 'null'
                action_text += f'{act} {slot} , '
            else:
                if orig_act in ['confirm']:
                    if not slot:
                        slot = 'null'
                    if not relation:
                        relation = 'null'
                else:
                    assert slot, action
                    assert relation, action

                action_text += f'{act} {slot} {relation} " {values} " , '

        action_text = action_text.strip(', ')

        return action_text

    def action2span(self, agent_actions, intents, setting):
        # compatible action2span for both BiToD and RiSAWOZ
        action_text = ''
        if isinstance(intents, list):
            pass
            # assert setting == "zh"  # temporary setting since translation is not ready yet
        else:
            intents = [intents]
        for intent in intents:
            intent_action_text = self.action2span_for_single_intent(agent_actions, intent, setting)
            action_text += intent_action_text
        return action_text.strip()  # retain the original output for BiToD

    def state2span(self, state):
        """
        converts dictionary of dialogue state to a text span
        :param dialogue_state: dict
        :return: str
        """

        if not state:
            return "null"
        span = ""

        # sort based on intent and then sort slots for each intent
        state = OrderedDict(sorted(state.items(), key=lambda s: s[0]))
        state = {k: OrderedDict(sorted(v.items(), key=lambda s: s[0])) for k, v in state.items()}

        def create_span(state, intent, slot):
            relation = state[intent][slot]["relation"]
            if isinstance(state[intent][slot]["value"], list):
                values = [str(value) for value in state[intent][slot]["value"]]
            else:
                # for RiSAWOZ
                values = [str(state[intent][slot]["value"])]
            values = sorted(values)
            values = " | ".join(values)
            span = f'{slot} {relation} " {values} " , '

            return span

        for intent in state:
            span += f"( {intent} ) "
            # check the required slots
            if intent not in self.value_mapping.required_slots:
                print(f'{intent} not in required slots!')
                continue
            if len(self.value_mapping.required_slots[intent]) > 0:
                for slot in self.value_mapping.required_slots[intent]:
                    if slot in state[intent]:
                        span += create_span(state, intent, slot)
                    else:
                        span += f"{slot} #unknown , "
            else:
                for slot in state[intent]:
                    span += create_span(state, intent, slot)
        return span.strip(', ')

    def compute_lev_span(self, previous_state, new_state, intent):
        Lev = f"( {intent} ) "
        if intent == "chat" or intent == "通用":
            return "null"
        old_state = copy.deepcopy(previous_state)
        if intent not in old_state:
            old_state[intent] = {}
        # TODO: annotation error of states in RiSAWOZ
        #       some states (not at begin of dialog) are empty
        #       I'll fix it later. Current solution is just a workaround.
        if intent not in new_state.keys():
            new_state[intent] = old_state[intent]

        for slot in new_state[intent]:
            if old_state[intent].get(slot) != new_state[intent].get(slot):
                relation = new_state[intent][slot]["relation"]
                if isinstance(new_state[intent][slot]["value"], list):
                    values = [str(value) for value in new_state[intent][slot]["value"]]
                else:
                    # for RiSAWOZ
                    values = [str(new_state[intent][slot]["value"])]
                values = " | ".join(values)
                Lev += f"{slot} {relation} \" {values} \" , "
        for slot in old_state[intent]:
            if slot not in new_state[intent]:
                print(f'slot: {old_state[intent][slot]} for intent: {intent} is missing in the new state')
                Lev += f"{slot} #unknown , "
        return Lev.strip(' ,')

    def span2knowledge(self, api_span):
        # reverse direction of knowledge2span fuction
        # converts knowledge span to knowledge dict

        knowledge = defaultdict(list)
        re_intent_spans = re.compile('\( (.*?) \)\s?(.*?)(?=$|\( )')
        re_svs = re.compile('(\S*? " .*? ")')

        matches = re_intent_spans.findall(api_span)

        for match in matches:
            intent, sv_span = match
            sv_matches = re_svs.findall(sv_span)
            for sv in sv_matches:
                try:
                    slot, value = sv.split(' ', 1)
                except Exception:
                    print(f'illegal syntax for slot-relation-values: {sv}')
                    exit(1)

                # remove " "
                value = value[2:-2]
                values = value.split(' | ')
                values = [convert_to_int(val) for val in values]
                knowledge[intent].append({"slot": slot, "value": values})

        return knowledge

    def knowledge2span(self, knowledge):
        if not knowledge:
            return 'null'

        # sort based on intent and then sort slots for each intent
        knowledge = OrderedDict(sorted(knowledge.items(), key=lambda s: s[0]))
        knowledge = {k: OrderedDict(sorted(v.items(), key=lambda s: s[0])) for k, v in knowledge.items()}

        knowledge_text = ""
        for intent, item in knowledge.items():
            knowledge_text += f"( {intent} ) "
            for slot, values in item.items():
                if slot not in self.value_mapping.skip_slots_for_kb:
                    if isinstance(values, list):
                        values_text = " | ".join(values)
                    else:
                        values_text = str(values)
                    if values_text == "":
                        values_text = "null"
                    knowledge_text += f"{slot} \" {values_text} \" , "
        return knowledge_text.strip(', ')

    def compute_da(self, preds, refs):
        da = 0.0
        for pred, ref in zip(preds, refs):
            if pred:
                pred = self.clean_value(pred)
                pred_dict = self.span2action(pred)

                ref = self.clean_value(ref)
                ref_dict = self.span2action(ref)

                if pred_dict == ref_dict:
                    da += 1
                else:
                    if self.DEBUG:
                        self.out_da.write(str(pred) + '\t' + str(ref) + '\t' + str(list(dictdiffer.diff(pred, ref))) + '\n')

        return da / len(preds) * 100

    def compute_ser(self, preds, act_values):
        ser = 0.0
        for pred, values in zip(preds, act_values):
            # remove emtpy slot values
            missing = False
            if len(values):
                for val in values:
                    if val in ['null', 'yes', 'no', 'true', 'false', '否', '是']:
                        continue
                    if str(val) not in pred:
                        missing = True
            if missing:
                ser += 1.0
                if self.DEBUG:
                    self.out_ser.write('\t'.join([pred, *values]) + '\n')
        return ser / len(preds) * 100

    def compute_dst_em(self, preds, golds):
        hit = 0
        for pred, gold in zip(preds, golds):
            pred_sets = self.convert_lists_to_set(pred)
            gold_sets = self.convert_lists_to_set(gold)

            if pred_sets == gold_sets:
                hit += 1
            else:
                if self.DEBUG:
                    self.out_dst.write(
                        str(pred_sets) + '\t' + str(gold_sets) + '\t' + str(list(dictdiffer.diff(pred_sets, gold_sets))) + '\n'
                    )

        return hit / len(preds) * 100

    def compute_success_rate(self, predictions, references):
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

                pred_sets = self.convert_lists_to_set_api(pred)
                constraints_sets = self.convert_lists_to_set_api(constraints)

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
            out = dial_id + '\t'
            dial_success_flag = True
            for response in predictions[dial_id]["turns"].values():
                responses += response["response"][0] + " "
            responses = self.clean_value(responses)
            out += responses + '\t' + ';;;' + '\t'

            for intent in references[dial_id]["tasks"]:
                if intent not in task_info:
                    task_info[intent] = {"total": 0, "hit": 0, "success_rate": 0}
                task_success_flag = True
                task_info[intent]["total"] += 1

                for entity in (
                    references[dial_id]["tasks"][intent]["inform+offer"] + references[dial_id]["tasks"][intent]["confirmation"]
                ):
                    entity = self.clean_value(entity)
                    if entity in ['null', 'yes', 'no', 'true', 'false', '否', '是']:
                        continue
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

            if out.split(';;;', 1)[1] != '\t':
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

    def clean_value(self, v, do_int=False):
        v = str(v)
        v = v.lower()
        v = v.strip()

        v = v.replace("，", ",")
        v = v.replace('..', '.')

        v = v.replace('；', ';')
        v = v.replace('。', '')

        # am, pm
        v = re.sub('(\d+)(?:[\.:](\d+))?\s?(?:pm )?(afternoon|in the afternoon|pm in the afternoon)', r'\1:\2 pm', v)
        v = re.sub('(\d+)(?:[\.:](\d+))?\s?(morning|in the morning|am in the morning)', r'\1:\2 am', v)
        v = re.sub('(\d+)(?:[\.:](\d+))?\s?(am|pm)', r'\1:\2 \3', v)

        v = re.sub('(\d+)\s?年\s?(\d+)\s?月\s?(\d+)', r'\1/\2/\3', v)
        if len(v) < 580:
            v = re.sub('(\d+)-?(\d+)?-?(\d+)?\s?\( (?:中国香港|中国大陆|韩国) \)?', r'\1/\2/\3', v)

        v = re.sub('(\d+)/0?(\d+)/0?(\d+)', r'\1/\2/\3', v)
        v = re.sub('(\d+)-0?(\d+)-0?(\d+)', r'\1/\2/\3', v)

        v = re.sub('(.*?) and (.*?) and (.*?)', r'\1,\2,\3', v)

        v = re.sub('(\d+)\.0', r'\1', v)

        # & --> and
        if self.name == 'bitod':
            v = re.sub(' [\&\/] ', ' and ', v)
        elif self.name == 'risawoz':
            v = re.sub(' \/ ', ',', v)

        v = re.sub('\s+', ' ', v)

        # remove extra dot in the end
        v = re.sub('(\d+)\.$', r'\1', v)
        v = re.sub('(\w+)\.$', r'\1', v)

        v = re.sub('(\w+)[。！？]$', r'\1', v)

        # 3rd of january --> januray 3
        v = re.sub('(\d+)(?:th|rd|st|nd) of (\w+)', r'\2 \1', v)

        # time consuming but needed step
        if not self.FAST_EVAL:
            for key, val in self.value_mapping.entity_map.items():
                key, val = str(key), str(val)
                if key in v:
                    v = v.replace(key, val)

        if do_int:
            v = convert_to_int(v, word2number=True)

        v = str(v)
        return v

    def convert_lists_to_set(self, state):
        new_state = copy.deepcopy(state)
        for i in state:
            for j in state[i]:
                for m, v in state[i][j].items():
                    if isinstance(v, list):
                        v = [self.clean_value(val, do_int=True) for val in v]
                        new_state[i][j][m] = set(v)
                    else:
                        new_state[i][j][m] = self.clean_value(v, do_int=True)
        return new_state

    def convert_lists_to_set_api(self, constraints):
        new_constraints = copy.deepcopy(constraints)
        if constraints:
            for k, v in constraints.items():
                if isinstance(v, dict):
                    for i, j in v.items():
                        if isinstance(j, list):
                            j = [self.clean_value(val, do_int=True) for val in j]
                            new_constraints[k][i] = set(j)
                        else:
                            new_constraints[k][i] = self.clean_value(j, do_int=True)
                else:
                    new_constraints[k] = self.clean_value(v, do_int=True)
        if new_constraints is None:
            new_constraints = {}
        return new_constraints

    def compute_result(self, predictions, reference_data):
        preds = []
        golds = []
        for dial_id in reference_data:
            pred_turn_id = 0
            for turn in reference_data[dial_id]["Events"]:
                if turn["Agent"] == "User":
                    pred_turn_id += 1

                    pred = predictions[dial_id]["turns"][str(pred_turn_id)]["state"]
                    # we record the string in genienlp instead of dict
                    # add fololoing for backward compatibility
                    if not isinstance(pred, dict):
                        pred = self.span2state(pred)
                    pred = {self.domain2api_name(k): v for k, v in pred.items()}
                    gold = turn["state"]

                    preds.append(pred)
                    golds.append(gold)

        jga = self.compute_dst_em(preds, golds)

        reference_task_success = defaultdict(dict)
        reference_act_values = []
        reference_actions = []
        reference_response = []
        predicted_response = []
        predicted_actions = []
        act_sets = set()
        for dial_id in reference_data:
            if dial_id not in reference_task_success:
                reference_task_success[dial_id]["tasks"] = {
                    self.value_mapping.zh_en_API_MAP.get(task["Task"], task["Task"]): {"inform+offer": [], "confirmation": []}
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
                        intent = [self.value_mapping.zh_en_API_MAP.get(turn["active_intent"], turn["active_intent"])]
                    else:
                        intent = turn["active_intent"]
                if turn["Agent"] == "Wizard":
                    if turn["Actions"] == "query":
                        if not isinstance(turn["API"], list):
                            # for compatibility of both BiTOD and RiSAWOZ
                            turn["API"] = [turn["API"]]
                            constraints = self.canonicalize_constraints(turn["Constraints"])
                        else:
                            # TODO: canonicalization for RiSAWOZ
                            constraints = turn["Constraints"]
                        for turn_api in turn["API"]:
                            turn_api = self.value_mapping.zh_en_API_MAP.get(turn_api, turn_api)
                            if constraints:
                                if turn_api in constraints.keys():
                                    # for RiSAWOZ: filter constraints with current API
                                    constraints = {k: v for k, v in constraints[turn_api].items()}
                                else:
                                    constraints = {k: v for k, v in constraints.items()}
                            reference_task_success[dial_id]["API"][turn_api] = constraints
                    else:
                        reference_response.append(self.clean_value(turn["Text"]))
                        act_values = set()
                        for item in turn["Actions"]:
                            if len(item["value"]):
                                if not isinstance(item["value"], list):
                                    item["value"] = [item["value"]]
                                for value in item["value"]:
                                    if not isinstance(value, list):
                                        value = [value]
                                    act_values.update(value)
                            act_values = set([self.clean_value(val) for val in act_values])
                        reference_act_values.append(act_values)

                        # for i in range(len(intent)):
                        #     # for RiSAWOZ: filter turn actions with current intent
                        #     turn_actions = (
                        #         [action for action in turn["Actions"] if action["domain"] == intent[i]]
                        #         if len(intent) > 1
                        #         else turn["Actions"]
                        #     )
                        #     reference_actions.append(
                        #         self.clean_value(
                        #             self.action2span(
                        #                 turn_actions, self.value_mapping.en_API_MAP.get(intent[i], intent[i]), 'en'
                        #             )
                        #         )
                        #     )

                        reference_actions.append(
                            self.clean_value(
                                self.action2span(
                                    turn["Actions"], [self.value_mapping.en_API_MAP.get(i, i) for i in intent], setting='en'
                                )
                            )
                        )

                        pred_rg = predictions[dial_id]["turns"][str(pred_turn_id)]["response"]
                        if isinstance(pred_rg, list):
                            assert len(pred_rg) == 1
                            pred_rg = pred_rg[0]
                        pred_rg = self.clean_value(pred_rg)
                        predicted_response.append(pred_rg)

                        pred_act = predictions[dial_id]["turns"][str(pred_turn_id)]["actions"]
                        if isinstance(pred_act, list):
                            assert len(pred_act) == 1
                            pred_act = pred_act[0]
                        pred_act = self.clean_value(pred_act)
                        predicted_actions.append(pred_act)

                        pred_turn_id += 1

                        # For each task, the last value for each slot are considered as final requested information from user
                        for action in turn["Actions"]:
                            if action["act"].lower() not in act_sets:
                                print(action["act"].lower())
                                act_sets.add(action["act"].lower())
                            trans_slot = action["slot"]
                            # should we include "recommend" ?
                            if (
                                (action["act"].lower() in ["inform", "offer"])
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
                if intent in ["general"]:  # for RiSAWOZ
                    continue
                for values in slot_values.values():
                    reference_task_success[dial_id]["tasks"][intent]["inform+offer"] += values
            for intent, slot_values in confirm_info.items():
                if intent in ["general"]:  # for RiSAWOZ
                    continue
                for values in slot_values.values():
                    reference_task_success[dial_id]["tasks"][intent]["confirmation"] += values

        success_rate, api_acc, task_info = self.compute_success_rate(predictions, reference_task_success)

        bleu = self.compute_bleu(predicted_response, reference_response)
        ser = self.compute_ser(predicted_response, reference_act_values)
        da_acc = self.compute_da(predicted_actions, reference_actions)

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

    def postprocess_text(self, preds, labels):
        preds = [pred.strip() for pred in preds]
        labels = [[label.strip()] for label in labels]

        return preds, labels

    def compute_bleu(self, preds, labels):
        """
        preds = [pred1, pred2,...]
        labels = [label1, label2,...]
        """
        # Some simple post-processing
        preds, labels = self.postprocess_text(preds, labels)

        bleu = metric.compute(predictions=preds, references=labels)["score"]
        bleu = round(bleu, 4)

        return bleu

    def translate_slots_to_english(self, text, do_translate=True):
        if not do_translate:
            return text
        for key, val in self.value_mapping.translation_dict.items():
            text = replace_word(text, key, val)
        for key, val in self.value_mapping.zh_API_MAP.items():
            text = replace_word(text, key, val)
        for key, val in zh2en_CARDINAL_MAP.items():
            text = text.replace(f'" {key} "', f'" {val} "')
        return text

    def get_dials_sequential(self, args, dials):
        all_dial_ids = list(dials.keys())
        few_dials_file = os.path.join(args.root, f"data/{args.setting}_fewshot_dials_{args.fewshot_percent}.json")

        if not os.path.exists(few_dials_file):
            dial_ids = all_dial_ids[: int(len(all_dial_ids) * args.fewshot_percent // 100)]
            print(f"few shot for {args.setting}, dialogue number: {len(dial_ids)}")
            with open(few_dials_file, "w") as f:
                json.dump({"fewshot_dials": dial_ids}, f, indent=True)
        else:
            with open(few_dials_file) as f:
                dial_ids = json.load(f)["fewshot_dials"]
        few_dials = {dial_id: dials[dial_id] for dial_id in dial_ids}
        dials = {dial_id: dials[dial_id] for dial_id in all_dial_ids if dial_id not in dial_ids}

        return dials, few_dials

    def get_dials_balanced(self, args, dials):
        all_dial_ids = list(dials.keys())
        few_dials_file = os.path.join(args.root, f"data/{args.setting}_fewshot_dials_{args.fewshot_percent}_balanced.json")

        if not os.path.exists(few_dials_file):
            dialogue_dominant_domains = defaultdict(list)
            domain_turn_counts = defaultdict(int)
            for dial_id, dial in dials.items():
                turn_domains = defaultdict(int)
                dialogue_turns = dial["Events"]

                for turn in dialogue_turns:
                    if turn["Agent"] == "User":
                        active_intent = self.value_mapping.API_MAP[turn["active_intent"]]

                        turn_domains[self.translate_slots_to_english(active_intent, args.english_slots)] += 1
                        domain_turn_counts[self.translate_slots_to_english(active_intent, args.english_slots)] += 1

                max_domain = max(turn_domains, key=turn_domains.get)
                dialogue_dominant_domains[max_domain].append(dial_id)

            total = sum(list(domain_turn_counts.values()))
            fewshot_dials = []
            for (domain, count) in domain_turn_counts.items():
                num_fewshot = int(len(all_dial_ids) * (count / total) * (args.fewshot_percent / 100))
                fewshot_dials += dialogue_dominant_domains[domain][:num_fewshot]
            print(f"balanced few shot for {args.setting}, dialogue number: {len(fewshot_dials)}")
            print("turn statistics:")
            for (domain, count) in domain_turn_counts.items():
                print(domain, "comprises of", count, "or", int(100 * count / total + 0.5), "percent")
            print("few-shot turn statistics:")
            res_turn_counts = defaultdict(int)
            for dial_id in fewshot_dials:
                for turn in dials[dial_id]["Events"]:
                    if turn["Agent"] == "User":
                        active_intent = self.value_mapping.API_MAP[turn["active_intent"]]
                        res_turn_counts[self.translate_slots_to_english(active_intent, args.english_slots)] += 1
            total = sum(list(res_turn_counts.values()))
            for (domain, count) in res_turn_counts.items():
                print(domain, "comprises of", count, "or", int(100 * count / total + 0.5), "percent")

            with open(few_dials_file, "w") as f:
                json.dump({"fewshot_dials": fewshot_dials}, f, indent=True)
                few_dial_ids = fewshot_dials
        else:
            with open(few_dials_file) as f:
                few_dial_ids = json.load(f)["fewshot_dials"]
        few_dials = {dial_id: dials[dial_id] for dial_id in few_dial_ids}
        dials = {dial_id: dials[dial_id] for dial_id in all_dial_ids if dial_id not in few_dial_ids}

        return dials, few_dials

    def read_data(self, args, path_names):
        print(("Reading all files from {}".format(path_names)))

        max_history = args.max_history
        setting = args.setting
        # read files
        for path_name in path_names:
            with open(path_name) as file:
                dials = json.load(file)

                data = []
                for dial_id, dial in tqdm(dials.items()):
                    dialogue_turns = dial["Events"]

                    dialog_history = []
                    knowledge = defaultdict(dict)
                    prev_knowledge = "null"
                    prev_state = {}
                    count = 1
                    turn_id = 0

                    while turn_id < len(dialogue_turns):
                        turn = dialogue_turns[turn_id]

                        if turn["Agent"] == "User":
                            if not isinstance(turn["active_intent"], list):
                                # for compatibility of both BiTOD and RiSAWOZ
                                turn["active_intent"] = [turn["active_intent"]]

                            intents = [self.value_mapping.API_MAP[intent] for intent in turn["active_intent"]]
                            task = ' / '.join([self.value_mapping.zh2en_INTENT_MAP.get(intent, intent) for intent in intents])

                            # accumulate dialogue utterances
                            if args.use_user_acts:
                                # TODO: risawoz has multiple
                                assert len(intents) == 1
                                action_text = self.action2span(turn["Actions"], intents[0], setting)
                                action_text = clean_text(action_text, is_formal=True)
                                action_text = self.translate_slots_to_english(action_text, args.english_slots)
                                dialog_history.append("USER_ACTS: " + action_text)
                            else:
                                dialog_history.append("USER: " + clean_text(turn["Text"]))

                            if args.last_two_agent_turns and len(dialog_history) >= 4:
                                dial_hist = [dialog_history[-4].replace('AGENT_ACTS:', 'AGENT_ACTS_PREV:')] + dialog_history[
                                    -2:
                                ]
                            else:
                                dial_hist = dialog_history[-max_history:]

                            dialog_history_text = " ".join(dial_hist)
                            dialog_history_text_for_api_da = dialog_history_text

                            if args.only_user_rg:
                                dialog_history_text_for_rg = dial_hist[-1]
                            else:
                                dialog_history_text_for_rg = dialog_history_text

                            # convert dict of slot-values into text
                            state_text = self.state2span(prev_state)

                            current_state = {self.value_mapping.API_MAP[k]: v for k, v in turn["state"].items()}
                            current_state = OrderedDict(sorted(current_state.items(), key=lambda s: s[0]))
                            current_state = {
                                k: OrderedDict(sorted(v.items(), key=lambda s: s[0])) for k, v in current_state.items()
                            }

                            if args.gen_full_state:
                                targets = []
                                for intent in current_state.keys():
                                    targets.append(self.compute_lev_span({}, current_state, intent))
                                target = ' '.join(targets)
                            elif args.gen_lev_span:
                                # compute the diff between old state and new state
                                assert len(intents) == 1
                                target = self.compute_lev_span(prev_state, current_state, intents[0])
                            else:
                                assert len(intents) == 1
                                target = self.compute_lev_span({}, current_state, intents[0])

                            if not target:
                                target = 'null'

                            input_text = " ".join(
                                [
                                    "DST:",
                                    "<state>",
                                    self.translate_slots_to_english(state_text, args.english_slots),
                                    "<endofstate>",
                                    "<history>",
                                    dialog_history_text,
                                    "<endofhistory>",
                                ]
                            )

                            input_text = clean_text(input_text, True)

                            dst_data_detail = {
                                "dial_id": dial_id,
                                "task": task,
                                "turn_id": count,
                                "input_text": input_text,
                                "output_text": self.translate_slots_to_english(target, args.english_slots),
                                "train_target": "dst",
                            }

                            if args.detail:
                                dst_data_detail["active_intent"] = intents[0]
                                dst_data_detail["prev_state"] = prev_state
                                dst_data_detail["current_state"] = current_state

                            data.append(dst_data_detail)

                            # update last dialogue state
                            prev_state = current_state

                            turn_id += 1

                        elif turn["Agent"] == "Wizard":
                            # convert dict of slot-values into text
                            state_text = self.state2span(prev_state)

                            input_text = " ".join(
                                [
                                    "API:",
                                    "<knowledge>",
                                    self.translate_slots_to_english(prev_knowledge, args.english_slots),
                                    "<endofknowledge>",
                                    "<state>",
                                    self.translate_slots_to_english(state_text, args.english_slots),
                                    "<endofstate>",
                                    "<history>",
                                    dialog_history_text_for_api_da,
                                    "<endofhistory>",
                                ]
                            )

                            input_text = clean_text(input_text, True)

                            if turn["Actions"] == "query":
                                # do api call
                                # next turn is KnowledgeBase
                                assert dialogue_turns[turn_id + 1]["Agent"] == 'KnowledgeBase'
                                next_turn = dialogue_turns[turn_id + 1]

                                if int(next_turn["TotalItems"]) == 0:
                                    # TODO: risawoz has multiple intents
                                    prev_knowledge = f"( {intents[0]} ) Message = No item available."
                                else:
                                    for intent in intents:
                                        if intent in next_turn["Item"]:
                                            knowledge[intent].update(next_turn["Item"][intent])
                                        # general intent, 1 erroneous turn in zh_train
                                        elif self.name == 'risawoz':
                                            if intent != 'general':
                                                print(f'intent: {intent} not found in next_turn KB. skipping...')
                                            continue
                                        else:
                                            knowledge[intent].update(next_turn["Item"])

                                    prev_knowledge = self.knowledge2span(knowledge)

                                api_data_detail = {
                                    "dial_id": dial_id,
                                    "task": task,
                                    "turn_id": count,
                                    "input_text": input_text,
                                    "output_text": "yes",
                                    "train_target": "api",
                                }

                                data.append(api_data_detail)

                                # skip knowledge turn since we already processed it
                                turn_id += 2
                                turn = dialogue_turns[turn_id]

                            else:

                                # no api call
                                api_data_detail = {
                                    "dial_id": dial_id,
                                    "task": task,
                                    "turn_id": count,
                                    "input_text": input_text,
                                    "output_text": "no",
                                    "train_target": "api",
                                }

                                data.append(api_data_detail)

                            input_text = " ".join(
                                [
                                    "DA:",
                                    "<knowledge>",
                                    self.translate_slots_to_english(prev_knowledge, args.english_slots),
                                    "<endofknowledge>",
                                    "<state>",
                                    self.translate_slots_to_english(state_text, args.english_slots),
                                    "<endofstate>",
                                    "<history>",
                                    dialog_history_text_for_api_da,
                                    "<endofhistory>",
                                ]
                            )

                            input_text = clean_text(input_text, True)

                            target = clean_text(turn["Text"])

                            action_text = self.action2span(turn["Actions"], intents, setting)
                            action_text = clean_text(action_text, is_formal=True)
                            action_text = self.translate_slots_to_english(action_text, args.english_slots)

                            acts_data_detail = {
                                "dial_id": dial_id,
                                "task": task,
                                "turn_id": count,
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
                                    dialog_history_text_for_rg,
                                    "<endofhistory>",
                                ]
                            )

                            response_data_detail = {
                                "dial_id": dial_id,
                                "task": task,
                                "turn_id": count,
                                "input_text": input_text,
                                "output_text": target,
                                "train_target": "rg",
                            }
                            data.append(response_data_detail)

                            # update dialogue history
                            if args.use_natural_response:
                                output_text = target
                            else:
                                output_text = action_text

                            dialog_history.append("AGENT_ACTS: " + output_text)

                            turn_id += 1
                            count += 1

        return data

    def prepare_data(self, args, path_train, path_dev, path_test):

        # "en, zh, en&zh, en2zh, zh2en"
        data_train, data_fewshot, data_dev, data_test = None, None, None, None

        if 'valid' in args.splits:
            data_dev = self.read_data(args, path_dev)
        if 'test' in args.splits:
            data_test = self.read_data(args, path_test)
        if 'train' in args.splits:
            train_data = self.read_data(args, path_train)
            with open(path_train[0]) as file:
                dials = json.load(file)

            if args.sampling == "sequential":
                train_dials, few_dials = self.get_dials_sequential(args, dials)
            else:
                train_dials, few_dials = self.get_dials_balanced(args, dials)
            data_train, data_fewshot = [], []
            for data in train_data:
                if data['dial_id'] in train_dials:
                    data_train.append(data)
                else:
                    data_fewshot.append(data)

        if args.setting == "en_zh":
            if data_train:
                random.shuffle(data_train)
            if data_dev:
                random.shuffle(data_dev)
            if data_test:
                random.shuffle(data_test)

        return data_train, data_fewshot, data_dev, data_test
