from collections import defaultdict

from dialogues import Bitod

api_names = ["restaurants_en_US_booking"]
dialogue_state = {
    "restaurants_en_US_booking": {
        "name": {"relation": "equal_to", "value": ["Mul Hayam"]},
        "time": {"relation": "equal_to", "value": ["3:10 pm"]},
        "date": {"relation": "equal_to", "value": ["April 17"]},
        "user_name": {"relation": "equal_to", "value": ["Aaron"]},
        "number_of_people": {"relation": "equal_to", "value": [7]},
    }
}

gold_knowledge_text = (
    '( restaurants_en_US_booking ) date " April 17 " , name " Mul Hayam " , number_of_people " 7 " ,'
    ' ref_number " 7S9BRVOL " , time " 3:10 pm " , user_name " Aaron "'
)

src_lang = 'en'
knowledge = defaultdict(dict)

dataset = Bitod()
knowledge_text, constraints = dataset.make_api_call(dialogue_state, knowledge, api_names, src_lang=src_lang)

assert gold_knowledge_text == knowledge_text
