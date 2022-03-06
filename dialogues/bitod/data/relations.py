import json
import re
from collections import defaultdict
from typing import Iterable


def dialogue_relations(dial: dict, relation_dict):
    dst = dial['output_text']
    domain_pat = "\( ((?:\w+) (?:\w+)) \)"
    words = "[\w|&]+(?: [\w|&]+)*"
    slot_rel_val = f"(\w+) (\w+) \" ({words}) \""
    pat = domain_pat + f"(?: {slot_rel_val}(?: , {slot_rel_val})*)?"
    m = re.match(pat, dst)
    if not m:
        return
    domain_relations = relation_dict[m.group(1)]
    i = 2
    while i < len(m.groups()):
        if not m.group(i):
            break
        assert m.group(i) and m.group(i + 1) and m.group(i + 2)
        domain_relations[m.group(i)].add(m.group(i + 1))
        i += 3


def read_json_file(file: str) -> Iterable[dict]:
    dic = json.load(open(file))['data']
    return dic


def print_combinations(rel_dict):
    combs = []
    for domain in rel_dict:
        for slot in rel_dict[domain]:
            for rel in rel_dict[domain][slot]:
                combs.append("{}!!{}!!{}!!@".format(domain.replace(" ", "-"), slot, rel))
    print('\n'.join(combs))


if __name__ == "__main__":
    for s in {"train", "valid", "test"}:

        dic = read_json_file(
            "/Users/shiningsunnyday/Documents/GitHub/dialogues/dialogues/bitod/data/preprocessed/zh2en_{}_v10.json".format(s)
        )
        rel_dict = defaultdict(lambda: defaultdict(set))

        for d in dic:
            if d["train_target"] == "dst":
                dialogue_relations(d, rel_dict)

    for domain in rel_dict:
        for slot in rel_dict[domain]:
            rel_dict[domain][slot] = list(rel_dict[domain][slot])

    print_combinations(rel_dict)

    json.dump(
        rel_dict,
        open(
            "/Users/shiningsunnyday/Documents/GitHub/dialogues/dialogues/bitod/data/preprocessed/zh2en_{}_v10_relations.json".format(
                s
            ),
            "w+",
        ),
    )
