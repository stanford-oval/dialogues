import copy
import re

from dialogues.main import convert_to_int

CJK_RANGES = [
    (ord(u"\u3300"), ord(u"\u33ff")),
    (ord(u"\ufe30"), ord(u"\ufe4f")),  # compatibility ideographs
    (ord(u"\uf900"), ord(u"\ufaff")),
    (ord(u"\U0002F800"), ord(u"\U0002fa1f")),  # compatibility ideographs
    (ord(u'\u3040'), ord(u'\u309f')),  # Japanese Hiragana
    (ord(u"\u30a0"), ord(u"\u30ff")),  # Japanese Katakana
    (ord(u"\u2e80"), ord(u"\u2eff")),  # cjk radicals supplement
    (ord(u"\u4e00"), ord(u"\u9fff")),
    (ord(u"\u3400"), ord(u"\u4dbf")),
    (ord(u"\U00020000"), ord(u"\U0002a6df")),
    (ord(u"\U0002a700"), ord(u"\U0002b73f")),
    (ord(u"\U0002b740"), ord(u"\U0002b81f")),
    (ord(u"\U0002b820"), ord(u"\U0002ceaf")),
]

CJK_ADDONS = [ord(u"\u3001"), ord('，'), ord('。'), ord('！'), ord('？')]


def is_cjk_char(cp):
    return cp in CJK_ADDONS or any([range[0] <= cp <= range[1] for range in CJK_RANGES])


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

        domain_constraints = {
            (k if lang == 'zh' else k.lower()): process_string(
                (v if lang == 'zh' else value_mapping.en2canonical.get(v, v)), lang
            )
            for k, v in domain_constraints.items()
        }

        if api == 'car':
            if 'number_of_seats' in domain_constraints:
                domain_constraints['number_of_seats'] = {"$gte": convert_to_int(domain_constraints['number_of_seats'])}

        db_name = f'{api_en}_{lang}'
        cursor = db[db_name].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            # matched["_id"] = str(matched["_id"])
            matched.pop("_id")
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
                        slot = slot if lang == "zh" else slot.lower()
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
