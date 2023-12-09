import logging
import os
import re

from pymongo import MongoClient

from ..main import WOZDataset
from .src.knowledgebase import api
from .src.knowledgebase.en_zh_mappings import BitodMapping
from ..utils import read_jsonl_files_in_folder

logger = logging.getLogger(__name__)


def build_bitod_db(db_json_path, api_map, mongodb_host=""):
    if mongodb_host:
        db_client = MongoClient(mongodb_host)
    else:
        db_client = MongoClient()
    bitod_db = db_client["bilingual_tod"]
    for db in bitod_db.list_collection_names():
        bitod_db[db].drop()

    raw_db = read_jsonl_files_in_folder(db_json_path)
    for domain in raw_db.keys():
        if api_map is None:
            col = bitod_db[domain]
        else:
            col = bitod_db[api_map[domain]]
        for i in range(len(raw_db[domain])):
            slot_list = list(raw_db[domain][i].keys())
            for s in slot_list:
                if "." in s:
                    # escape dot cause mongodb doesn't like '.' and '$' in key names
                    raw_db[domain][i][s.replace(".", "\uFF0E")] = raw_db[domain][i].pop(s)
        col.insert_many(raw_db[domain], ordered=True)
    return bitod_db



class Bitod(WOZDataset):
    def __init__(self, name='bitod'):
        super().__init__(name)

        self.value_mapping = BitodMapping()
        
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        mongodb_host = "mongodb://localhost:27017/"
        bitod_db = build_bitod_db(
            db_json_path=os.path.join(*[cur_dir, f'database/db/bilingual_tod']),
            api_map=None,
            mongodb_host=mongodb_host,
        )

        db = {"null": None}
        self.skipped_entities = set()

        for domain in ['restaurants', 'hotels']:
            for lang in ['en_US', 'zh_CN']:
                db[f"{domain}_{lang}_booking"] = bitod_db[f"{domain}_{lang}"]
                db[f"{domain}_{lang}_search"] = bitod_db[f"{domain}_{lang}"]

        for domain in ['attractions', 'weathers']:
            for lang in ['en_US', 'zh_CN']:
                db[f"{domain}_{lang}_search"] = bitod_db[f"{domain}_{lang}"]

        self.db = db

    def domain2api_name(self, domain):
        # TODO: update
        return self.value_mapping.r_en_API_MAP.get(domain, domain)

    def make_api_call(self, dialogue_state, knowledge, api_names, src_lang='en', dial_id=None, turn_id=None):
        # bitod only does api call for the last (active) intent
        assert isinstance(api_names, list)
        api_name = api_names[-1]

        constraints = self.state2constraints(dialogue_state[api_name])

        count = 0
        processed_query = ''

        try:
            result, count, processed_query = api.call_api(self.db, api_name, constraints=[constraints], lang=src_lang)
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
            new_knowledge_text = self.knowledge2span(knowledge)

        return new_knowledge_text, {self.domain2api_name(api_name): constraints}

    def postprocess_prediction(self, prediction, knowledge=None, lang='en'):
        if re.search(rf'\( HKMTR {lang} \)', prediction):
            action_dict = self.span2action(prediction)
            domain = f'HKMTR {lang}'
            metro_slots = set(item['slot'] for item in action_dict[domain])
            for slot in ['estimated_time', 'price']:
                if knowledge and slot in knowledge[domain] and slot not in metro_slots:
                    action_dict[domain].append(
                        {'act': 'offer', 'slot': slot, 'relation': 'equal_to', 'value': [knowledge[domain][slot]]}
                    )

            prediction = self.action2span(action_dict[domain], domain, lang)

        if re.search(r'\( weathers search \)', prediction):
            action_dict = self.span2action(prediction)
            domain = 'weathers search'
            weather_slots = set(item['slot'] for item in action_dict[domain])
            for slot in ['max_temp', 'min_temp', 'weather', 'city']:
                if knowledge and slot in knowledge[domain] and slot not in weather_slots:
                    action_dict[domain].append(
                        {'act': 'offer', 'slot': slot, 'relation': 'equal_to', 'value': [knowledge[domain][slot]]}
                    )

            prediction = self.action2span(action_dict[domain], domain, lang)

        return prediction
