import copy
import json
import os
import re
from collections import OrderedDict, defaultdict

from word2number import w2n

from dialogues.bitod.src.knowledgebase import api
from dialogues.bitod.src.knowledgebase.en_zh_mappings import (
    API_MAP,
    en2zh_ACT_MAP,
    en2zh_RELATION_MAP,
    en2zh_SLOT_MAP,
    en2zh_VALUE_MAP,
    en_API_MAP,
    entity_map,
    reverse_entity_map,
    zh2en_SLOT_MAP,
    zh2en_VALUE_MAP,
    zh_en_API_MAP,
)


def convert_to_int(val, strict=False, word2number=False):
    val = str(val)
    if val.isdigit() and not val.startswith('0'):
        return int(val)
    elif word2number and len(val.split()) == 1:
        # elif word2number:
        try:
            num = w2n.word_to_num(val)
            return num
        except:
            if strict:
                return None
            else:
                return val
    else:
        if strict:
            return None
        else:
            return val


def span2state(state_span, api_names):
    # reverse direction of state2span function
    # converts text span to state dict

    state = defaultdict(dict)
    re_intent_spans = re.compile('\( (.*?) \)\s?(.*?)(?=$|\( )')
    re_srvs = re.compile('(\S*? \S*? " .*? "|\S*? #unknown)')

    matches = re_intent_spans.findall(state_span)

    for match in matches:
        intent, srv_span = match
        state[intent] = {}
        if intent in api_names:
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


def state2constraints(dict_data):
    # converts dialogue state to constraints canonical form
    constraints = {}
    for slot, r_v in dict_data.items():
        if r_v["value"] == ["don't care"] or r_v["value"] == ["不在乎"]:
            continue
        relation = r_v["relation"]
        values = r_v["value"]
        if relation != "one_of" and relation != en2zh_RELATION_MAP["one_of"]:
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
        if relation == "one_of" or relation == en2zh_RELATION_MAP["one_of"]:
            constraints[slot] = api.is_one_of(values)
        elif relation == "at_least" or relation == en2zh_RELATION_MAP["at_least"]:
            constraints[slot] = api.is_at_least(values)
        elif relation == "not" or relation == en2zh_RELATION_MAP["not"]:
            constraints[slot] = api.is_not(values)
        elif relation == "less_than" or relation == en2zh_RELATION_MAP["less_than"]:
            constraints[slot] = api.is_less_than(values)
        else:
            constraints[slot] = api.is_equal_to(values)
    return constraints


def is_int(val):
    try:
        _ = int(val)
    except ValueError:
        return False
    return True


def canonicalize_constraints(dict_data):
    # converts the constraints dictionary in the original data to canonical form
    constraints = {}
    for const in dict_data:
        for slot, values in const.items():
            relation = values[values.find(".") + 1 : values.find("(")]
            values = values[values.find("(") + 1 : -1]
            values = values.replace('in the afternoon', 'pm')
            values = values.replace(' and ', ' & ')
            values = entity_map.get(values, values)

            if relation == "one_of" or relation == en2zh_RELATION_MAP["one_of"]:
                values = values.split(" , ")
                # values.sort()
            else:
                # values = int(values) if is_int(values) else values
                values = convert_to_int(values, word2number=True)
            if relation == "one_of" or relation == en2zh_RELATION_MAP["one_of"]:
                constraints[slot] = api.is_one_of(values)
            elif relation == "at_least" or relation == en2zh_RELATION_MAP["at_least"]:
                constraints[slot] = api.is_at_least(values)
            elif relation == "not" or relation == en2zh_RELATION_MAP["not"]:
                constraints[slot] = api.is_not(values)
            elif relation == "less_than" or relation == en2zh_RELATION_MAP["less_than"]:
                constraints[slot] = api.is_less_than(values)
            else:
                constraints[slot] = api.is_equal_to(values)
    constraints = OrderedDict(sorted(constraints.items()))
    if constraints == {}:
        constraints = None
    return constraints


def read_ontology(tgt_lang):
    all_ontologies = defaultdict(lambda: defaultdict(set))
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for fn in os.listdir(os.path.join(cur_dir, "knowledgebase/apis")):
        api_name = fn.replace(".json", "")
        _, rest = api_name.split('_', 1)
        lang = rest[:2]
        if lang != tgt_lang[:2]:
            continue

        api_name = API_MAP[api_name]

        with open(os.path.join(cur_dir, "knowledgebase/apis", fn)) as f:
            ontology = json.load(f)
            processed_ont = defaultdict(set)
            for key in ['input', 'output']:
                for item in ontology[key]:
                    slot, type = item['Name'], item['Type']
                    if lang == 'zh':
                        slot = en2zh_SLOT_MAP[slot]
                    if type == 'Categorical':
                        values = item['Categories']
                        values += [entity_map.get(val, val) for val in values]
                        values += [reverse_entity_map.get(val, val) for val in values]
                        values = set(values)
                        processed_ont[slot].update(values)
                    elif type == 'Integer':
                        values = list(range(item['Min'], item['Max'] + 1))
                        values += [entity_map.get(val, val) for val in values]
                        values += [reverse_entity_map.get(val, val) for val in values]
                        values = set(values)
                        processed_ont[slot].update(values)
                    else:
                        raise ValueError('bad type')

            all_ontologies[api_name] = processed_ont

    return all_ontologies


def span2action(api_span, api_names):
    # reverse direction of state2span fuction
    # converts text span to state dict

    action = defaultdict(list)
    re_intent_spans = re.compile('\( (.+?) \)\s?(.+?)(?=$|\( )')
    re_asrs = re.compile('((?:\S+? ){3}" .+? "|\S*? \S+?(?: ,|$)|\S+?(?: ,|$))')

    matches = re_intent_spans.findall(api_span)

    for match in matches:
        intent, srv_span = match
        if intent in api_names:
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


def action2span(agent_actions, intent, setting):
    action_text = f'( {intent} ) '

    # sort based on act, then slot
    agent_actions = list(sorted(agent_actions, key=lambda s: (s['act'], s['slot'])))

    for action in agent_actions:
        act, slot, relation, values = action['act'], action['slot'], action['relation'], action['value']

        orig_act = act
        if setting == 'zh':
            act = en2zh_ACT_MAP[act]

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
        ]:
            action_text += f'{act} , '
        elif orig_act in ['request', 'request_update']:
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


def state2span(state, required_slots):
    if not state:
        return "null"
    span = ""

    # sort based on intent and then sort slots for each intent
    state = OrderedDict(sorted(state.items(), key=lambda s: s[0]))
    state = {k: OrderedDict(sorted(v.items(), key=lambda s: s[0])) for k, v in state.items()}

    for intent in state:
        span += f"( {intent} ) "
        # check the required slots
        if intent not in required_slots:
            print(f'{intent} not in required slots!')
            continue
        if len(required_slots[intent]) > 0:
            for slot in required_slots[intent]:
                if slot in state[intent]:
                    relation = state[intent][slot]["relation"]
                    values = [str(value) for value in state[intent][slot]["value"]]
                    values = sorted(values)
                    values = " | ".join(values)
                    span += f"{slot} {relation} \" {values} \" , "
                else:
                    span += f"{slot} #unknown , "
        else:
            for slot in state[intent]:
                relation = state[intent][slot]["relation"]
                values = [str(value) for value in state[intent][slot]["value"]]
                values = sorted(values)
                values = " | ".join(values)
                span += f"{slot} {relation} \" {values} \" , "
    return span.strip(', ')


def compute_lev_span(previous_state, new_state, intent):
    Lev = f"( {intent} ) "
    if intent == "chat":
        return "null"
    old_state = copy.deepcopy(previous_state)
    if intent not in old_state:
        old_state[intent] = {}
    for slot in new_state[intent]:
        if old_state[intent].get(slot) != new_state[intent].get(slot):
            relation = new_state[intent][slot]["relation"]
            values = [str(value) for value in new_state[intent][slot]["value"]]
            values = " | ".join(values)
            Lev += f"{slot} {relation} \" {values} \" , "
    for slot in old_state[intent]:
        if slot not in new_state[intent]:
            print(intent, old_state[intent][slot])
            Lev += f"{slot} #unkown , "
    return Lev.strip(' ,')


def span2knowledge(api_span):
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


def knowledge2span(knowledge):
    if not knowledge:
        return 'null'

    # sort based on intent and then sort slots for each intent
    knowledge = OrderedDict(sorted(knowledge.items(), key=lambda s: s[0]))
    knowledge = {k: OrderedDict(sorted(v.items(), key=lambda s: s[0])) for k, v in knowledge.items()}

    knowledge_text = ""
    for intent, item in knowledge.items():
        knowledge_text += f"( {intent} ) "
        for slot, values in item.items():
            if slot not in ["type", "description", "类别", "描述"]:
                if isinstance(values, list):
                    values_text = " | ".join(values)
                else:
                    values_text = str(values)
                if values_text == "":
                    values_text = "null"
                knowledge_text += f"{slot} \" {values_text} \" , "
    return knowledge_text.strip(', ')


def create_mixed_lang_text(input, output, pretraining_prefix):
    if pretraining_prefix == "en2zh_trainsfer":
        for k, v in en_API_MAP.items():
            input = input.replace(f" {v}", f" {k}")
            output = output.replace(f" {v}", f" {k}")
        for k, v in zh_en_API_MAP.items():
            input = input.replace(f" {v}", f" {k}")
            output = output.replace(f" {v}", f" {k}")
        for k, v in zh2en_SLOT_MAP.items():
            input = input.replace(f" {v}", f" {k}")
            output = output.replace(f" {v}", f" {k}")
        for k, v in en2zh_RELATION_MAP.items():
            input = input.replace(f" {k}", f" {v}")
            output = output.replace(f" {k}", f" {v}")
        for k, v in en2zh_VALUE_MAP.items():
            input = input.replace(f" {k}", f" {v}")
            output = output.replace(f" {k}", f" {v}")
    elif pretraining_prefix == "zh2en_trainsfer":
        for k, v in en_API_MAP.items():
            input = input.replace(f" {k}", f" {v}")
            output = output.replace(f" {k}", f" {v}")
        for k, v in zh_en_API_MAP.items():
            input = input.replace(f" {k}", f" {v}")
            output = output.replace(f" {k}", f" {v}")
        for k, v in zh2en_SLOT_MAP.items():
            input = input.replace(f" {k}", f" {v}")
            output = output.replace(f" {k}", f" {v}")
        for k, v in en2zh_RELATION_MAP.items():
            input = input.replace(f" {v}", f" {k}")
            output = output.replace(f" {v}", f" {k}")
        for k, v in zh2en_VALUE_MAP.items():
            input = input.replace(f" {k}", f" {v}")
            output = output.replace(f" {k}", f" {v}")

    return input, output


def clean_text(text, is_formal=False):
    text = text.strip()
    text = re.sub(' +', ' ', text)
    text = re.sub('\\n|\\t', ' ', text)

    if not is_formal:
        text = text.replace('"', '')

    return text
