import logging
import os.path
import re

from ..main import Dataset
from .src.evaluate import eval_file
from .src.knowledgebase import api
from .src.knowledgebase.en_zh_mappings import BitodMapping
from .src.preprocess import prepare_data
from .src.utils import action2span, knowledge2span, span2action, span2knowledge, span2state, state2constraints, state2span

logger = logging.getLogger(__name__)

value_mapping = BitodMapping()


class Bitod(Dataset):
    def __init__(self, name='bitod'):
        super().__init__(name)

    def domain2api_name(self, domain):
        # TODO: update
        return value_mapping.r_en_API_MAP.get(domain, domain)

    def state2span(self, dialogue_state):
        return state2span(dialogue_state, value_mapping.required_slots)

    def span2state(self, state_text):
        return span2state(state_text, value_mapping.api_names)

    def knowledge2span(self, knowledge):
        return knowledge2span(knowledge)

    def span2knowledge(self, knowledge_text):
        return span2knowledge(knowledge_text)

    def update_state(self, lev, cur_state):
        for api_name in lev:
            if api_name not in cur_state:
                cur_state[api_name] = lev[api_name]
            else:
                cur_state[api_name].update(lev[api_name])

    def process_data(self, args):
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

        train, fewshot, dev, test = prepare_data(args, path_train, path_dev, path_test)
        return train, fewshot, dev, test

    def make_api_call(self, dialogue_state, knowledge, api_names, src_lang='en', dial_id=None, turn_id=None):
        # bitod only does api call for the last (active) intent
        assert isinstance(api_names, list)
        api_name = api_names[-1]

        constraints = state2constraints(dialogue_state[api_name])

        try:
            result, count, processed_query = api.call_api(api_name, constraints=[constraints], lang=src_lang)
        except Exception as e:
            logger.error(f'Error: {e}')
            logger.error(
                f'Failed API call with api_name: {str(api_name)}, constraints: {constraints}, processed_query: {processed_query}, for turn: {dial_id}/{turn_id}'
            )

        if int(count) <= 0:
            logger.warning(
                f'Message = No item available for api_name: {api_name}, constraints: {constraints},'
                f' processed_query: {processed_query}, for turn: {dial_id}/{turn_id}'
            )
            new_knowledge_text = f'( {api_name} ) Message = No item available.'
        else:
            # always choose the highest ranking results (so we have deterministic api results)
            knowledge[api_name].update(result)
            new_knowledge_text = knowledge2span(knowledge)

        return new_knowledge_text, {self.domain2api_name(api_name): constraints}

    def compute_metrics(self, args, prediction_path, reference_path):
        results = eval_file(args, prediction_path, reference_path)
        return results

    def do_knowledge_reset(self, api_name):
        do_reset = False
        if api_name and 'HKMTR' not in api_name:
            do_reset = True
        return do_reset

    def postprocess_prediction(self, prediction, knowledge=None, lang='en'):
        if re.search(rf'\( HKMTR {lang} \)', prediction):
            action_dict = span2action(prediction, value_mapping.api_names)
            domain = f'HKMTR {lang}'
            metro_slots = set(item['slot'] for item in action_dict[domain])
            for slot in ['estimated_time', 'price']:
                if knowledge and slot in knowledge[domain] and slot not in metro_slots:
                    action_dict[domain].append(
                        {'act': 'offer', 'slot': slot, 'relation': 'equal_to', 'value': [knowledge[domain][slot]]}
                    )

            prediction = action2span(action_dict[domain], domain, lang)

        if re.search(r'\( weathers search \)', prediction):
            action_dict = span2action(prediction, value_mapping.api_names)
            domain = 'weathers search'
            weather_slots = set(item['slot'] for item in action_dict[domain])
            for slot in ['max_temp', 'min_temp', 'weather', 'city']:
                if knowledge and slot in knowledge[domain] and slot not in weather_slots:
                    action_dict[domain].append(
                        {'act': 'offer', 'slot': slot, 'relation': 'equal_to', 'value': [knowledge[domain][slot]]}
                    )

            prediction = action2span(action_dict[domain], domain, lang)

        return prediction
