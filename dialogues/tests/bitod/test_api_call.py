from collections import defaultdict

import dictdiffer

from dialogues import Bitod

api_name = "restaurants_en_US_booking"
dialogue_state = {
    "restaurants_en_US_booking": {
        "name": {"relation": "equal_to", "value": ["Mul Hayam"]},
        "time": {"relation": "equal_to", "value": ["3:10 pm"]},
        "date": {"relation": "equal_to", "value": ["April 17"]},
        "user_name": {"relation": "equal_to", "value": ["Aaron"]},
        "number_of_people": {"relation": "equal_to", "value": [7]},
    }
}
src_lang = 'en'
knowledge = defaultdict(dict)


dataset = Bitod()
knowledge = dataset.make_api_call(dialogue_state, api_name, src_lang)
gold_knowkedge = {
    api_name: {
        "name": "Mul Hayam",
        "ref_number": "7S9BRVOL",
        "user_name": "Aaron",
        "number_of_people": 7,
        "time": "3:10 pm",
        "date": "April 17",
    }
}

print(knowledge)
print('diff:', list(dictdiffer.diff(knowledge, gold_knowkedge)))
