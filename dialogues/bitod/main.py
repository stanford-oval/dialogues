import logging
import re

from pymongo import MongoClient

from ..main import WOZDataset
from .src.knowledgebase import api
from .src.knowledgebase.en_zh_mappings import BitodMapping

logger = logging.getLogger(__name__)


class Bitod(WOZDataset):
    def __init__(self, name='bitod'):
        super().__init__(name)

        self.value_mapping = BitodMapping()

        mongodb_host = 'mongodb+srv://bitod:plGYPp44hASzGbmm@cluster0.vo7pq.mongodb.net/bilingual_tod?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE'
        client = MongoClient(mongodb_host, authSource='admin')
        database = client["bilingual_tod"]

        db = {"null": None}

        for domain in ['restaurants', 'hotels']:
            for lang in ['en_US', 'zh_CN']:
                db[f"{domain}_{lang}_booking"] = database[f"{domain}_{lang}"]
                db[f"{domain}_{lang}_search"] = database[f"{domain}_{lang}"]

        for domain in ['attractions', 'weathers']:
            for lang in ['en_US', 'zh_CN']:
                db[f"{domain}_{lang}_search"] = database[f"{domain}_{lang}"]

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
