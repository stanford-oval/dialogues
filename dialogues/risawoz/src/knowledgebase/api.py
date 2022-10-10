import copy
import re

from genienlp.data_utils.almond_utils import is_cjk_char


def call_api(db, api_names, constraints, lang, value_mapping, actions=None):
    knowledge = {}
    for api in api_names:
        api_en = value_mapping.zh2en_DOMAIN_MAP.get(api, api)
        # if api not in constraints:
        #     continue
        knowledge[api] = {}
        if api not in constraints:
            domain_constraints = {}
        else:
            domain_constraints = copy.deepcopy(constraints[api])

        domain_constraints = {k: value_mapping.en2canonical.get(v, v) for k, v in domain_constraints.items()}

        if api == 'car':
            if 'number_of_seats' in domain_constraints:
                domain_constraints['number_of_seats'] = {"$gte": int(domain_constraints['number_of_seats'])}

        db_name = f'{api_en}_{lang}'
        cursor = db[db_name].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            matched["_id"] = str(matched["_id"])
            # for key, val in matched.items():
            #     matched[key] = process_string(val)
            domain_knowledge.append(matched)
        if domain_knowledge:
            if actions:
                acts = actions[api]
                for item in domain_knowledge:
                    found = True
                    for slot, value in acts.items():
                        slot = slot.replace('.', '\uFF0E')
                        slot = slot.replace(' ', '_')
                        slot = slot.lower()
                        slot = value_mapping.zh2en_SLOT_MAP.get(slot, slot)
                        if slot not in item:
                            if slot == 'price' and api_en == 'car':
                                slot = 'price(ten_thousand_yuan)'
                            if slot == 'opening_hours' and api_en == 'restaurant':
                                slot = 'business_hours'
                        if slot not in item:
                            print(slot)
                        if item[slot] not in value:
                            found = False
                    if found:
                        knowledge[api] = item
                        break

            # if failed return first result
            # keep only the first result
            if not knowledge[api]:
                knowledge[api] = domain_knowledge[0]

            knowledge[api]["available_options"] = len(domain_knowledge)
    return knowledge


def tokenize_string(sentence):
    output = []
    i = 0
    while i < len(sentence):
        output.append(sentence[i])
        # skip space between cjk chars
        if (
            is_cjk_char(ord(sentence[i]))
            and i + 1 < len(sentence)
            and sentence[i + 1] == ' '
            and i + 2 < len(sentence)
            and is_cjk_char(ord(sentence[i + 2]))
        ):
            i += 1
        elif is_cjk_char(ord(sentence[i])) and i + 1 < len(sentence) and not is_cjk_char(ord(sentence[i + 1])):
            output.append(' ')
        elif not is_cjk_char(ord(sentence[i])) and i + 1 < len(sentence) and is_cjk_char(ord(sentence[i + 1])):
            output.append(' ')
        i += 1

    output = "".join(output)
    output = re.sub(r'\s{2,}', ' ', output)

    return output


def process_string(sentence, setting):
    if isinstance(sentence, bool):
        return str(sentence)
    if not isinstance(sentence, str):
        return sentence
    sentence = re.sub(r'\s{2,}', ' ', sentence)
    if setting == 'zh':
        sentence = ''.join(sentence.split())
    sentence = tokenize_string(sentence)

    return sentence
