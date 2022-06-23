import logging
import os.path

from ..bitod.src.evaluate import eval_file
from ..bitod.src.preprocess import prepare_data
from ..bitod.src.utils import knowledge2span, span2state, state2constraints, state2span
from ..main import Dataset
from .src.knowledgebase import api
from .src.knowledgebase.en_zh_mappings import api_names, required_slots

logger = logging.getLogger(__name__)


class Risawoz(Dataset):
    def __init__(self, name='RiSAWOZ'):
        super().__init__(name)

    def domain2api_name(self, domain):
        return domain

    def state2span(self, dialogue_state):
        return state2span(dialogue_state, required_slots)

    def span2state(self, lev):
        return span2state(lev, api_names)

    def update_state(self, lev, cur_state):
        for api_name in lev:
            if api_name not in cur_state:
                cur_state[api_name] = lev[api_name]
            else:
                cur_state[api_name].update(lev[api_name])

    def process_data(self, args, root):
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

        path_train = [os.path.join(root, p) for p in path_train]
        path_dev = [os.path.join(root, p) for p in path_dev]
        path_test = [os.path.join(root, p) for p in path_test]

        train, fewshot, dev, test = prepare_data(args, path_train, path_dev, path_test)
        return train, fewshot, dev, test

    def make_api_call(
        self,
        dialogue_state,
        knowledge,
        api_names,
        src_lang='zh_CN',
        dial_id=None,
        turn_id=None,
    ):
        constraints = {}
        for api_name in dialogue_state.keys():
            constraints[api_name] = state2constraints(dialogue_state[api_name])
        new_knowledge_text = 'null'

        try:
            result = api.call_api(api_names, constraints, lang=src_lang)
            # remove _id
            # result = [result[0], {api_name: result[0][api_name]["可用选项"] for api_name in result[0].keys()}]
            for api_name in result.keys():
                result[api_name].pop('_id', None)

        except Exception as e:
            logger.error(f'Error: {e}')
            logger.error(
                f'Failed API call with api_name: {str(api_names)}, constraints: {constraints}, for turn: {dial_id}/{turn_id}'
            )
        for api_name in result.keys():
            if int(len(result[api_name])) <= 0:
                logger.warning(
                    f'Message = No item available for api_name: {api_name}, constraints: {constraints},'
                    f' for turn: {dial_id}/{turn_id}'
                )
                new_knowledge_text = f'( {api_name} ) Message = No item available.'
            else:
                knowledge.update(result)
                new_knowledge_text = knowledge2span(knowledge)

        return new_knowledge_text, constraints

    def compute_metrics(self, args, prediction_path, reference_path):
        results = eval_file(args, prediction_path, reference_path)
        return results

    def postprocess_prediction(self, prediction, knowledge=None, lang='en'):
        return prediction
