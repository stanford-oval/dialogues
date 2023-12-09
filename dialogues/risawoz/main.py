import logging
import os

from pymongo import MongoClient

from ..main import WOZDataset
from .src.knowledgebase import api
from .src.knowledgebase.en_zh_mappings import RisawozMapping
from ..utils import read_json_files_in_folder

logger = logging.getLogger(__name__)


def build_risawoz_db(db_json_path, api_map, mongodb_host=""):
    if mongodb_host:
        db_client = MongoClient(mongodb_host)
    else:
        db_client = MongoClient()
    risawoz_db = db_client["risawoz"]
    for db in risawoz_db.list_collection_names():
        risawoz_db[db].drop()

    for lang in ['en', 'fr', 'hi', 'ko', 'zh', 'enhi']:
        folder = f'db_{lang}'
        raw_db = read_json_files_in_folder(os.path.join(db_json_path, folder))
        for domain in raw_db.keys():
            if api_map is None:
                col = risawoz_db[domain]
            else:
                col = risawoz_db[api_map[domain]]
            for i in range(len(raw_db[domain])):
                slot_list = list(raw_db[domain][i].keys())
                for s in slot_list:
                    if "." in s:
                        # escape dot cause mongodb doesn't like '.' and '$' in key names
                        raw_db[domain][i][s.replace(".", "\uFF0E")] = raw_db[domain][i].pop(s)
            col.insert_many(raw_db[domain], ordered=True)
    return risawoz_db


class Risawoz(WOZDataset):
    def __init__(self, name='risawoz', src='zh', tgt='en', mongodb_host=None):
        super().__init__(name)

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        mongodb_host = "mongodb://localhost:27017/"
        risawoz_db = build_risawoz_db(
            db_json_path=os.path.join(*[cur_dir, f'database/']),
            api_map=None,
            mongodb_host=mongodb_host,
        )
        self.db = risawoz_db

        tgt = tgt.split('_', 1)[0]
        src = src.split('_', 1)[0]

        if tgt == 'en':
            src = 'zh'
        else: # ['fr', 'hi', 'enhi', 'ko']
            src = 'en'

        self.value_mapping = RisawozMapping(src=src, tgt=tgt)
        self.skipped_entities = {
            'null',
            'yes',
            'no',
            'true',
            'false',
            '否',
            '是',
            'has',
            'can',
            'can\'t',
            'could',
            'yes',
            'be',
            'do',
            'have',
            'does not have',
            'available',
            'can get there directly',
            'can\'t get there directly',
            'can\'t get there directly by subway',
            'no subway stations',
            'yes, you can' 'get there directly by subway',
            'no direct subway',
            'ye',
            'non',
            'oui',
        }

        self._warnings = set()

    def domain2api_name(self, domain):
        return domain

    def make_api_call(
        self,
        dialogue_state,
        knowledge,
        api_names,
        src_lang='zh',
        dial_id=None,
        turn_id=None,
    ):
        src_lang = src_lang.split('_', 1)[0]
        constraints = {}
        for api_name in dialogue_state.keys():
            constraints[api_name] = self.state2constraints(dialogue_state[api_name])
        new_knowledge_text = 'null'

        try:
            result = api.call_api(self.db, api_names, constraints, src_lang, self.value_mapping)

        except Exception as e:
            logger.error(f'Error: {e}')
            logger.error(
                f'Failed API call with api_name: {str(api_names)}, constraints: {constraints}, for turn: {dial_id}/{turn_id}'
            )
        for api_name in result.keys():
            if int(len(result[api_name])) <= 0:
                warning = f'Message = No item available for api_name: {api_name}, constraints: {constraints}'
                if warning not in self._warnings:
                    logger.warning(warning + f', for turn: {dial_id}/{turn_id}')
                    self._warnings.add(warning)
                new_knowledge_text = f'( {api_name} ) Message = No item available.'
            else:
                knowledge.update(result)
                new_knowledge_text = self.knowledge2span(knowledge)

        return new_knowledge_text, constraints
