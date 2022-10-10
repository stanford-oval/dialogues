import logging

from pymongo import MongoClient

from ..main import WOZDataset
from .src.knowledgebase import api
from .src.knowledgebase.en_zh_mappings import RisawozMapping

logger = logging.getLogger(__name__)


class Risawoz(WOZDataset):
    def __init__(self, name='risawoz'):
        super().__init__(name)

        mongodb_host = 'mongodb+srv://bitod:plGYPp44hASzGbmm@cluster0.vo7pq.mongodb.net/risawoz?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE'
        client = MongoClient(mongodb_host, authSource='admin')

        self.db = client["risawoz"]

        self.value_mapping = RisawozMapping()

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
        constraints = {}
        for api_name in dialogue_state.keys():
            constraints[api_name] = self.state2constraints(dialogue_state[api_name])
        new_knowledge_text = 'null'

        try:
            result = api.call_api(self.db, api_names, constraints, src_lang, self.value_mapping)
            # remove _id
            # for api_name in result.keys():
            #     result[api_name].pop('_id', None)

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
                # new_knowledge_text = 'null'
            else:
                knowledge.update(result)
                new_knowledge_text = self.knowledge2span(knowledge)

        return new_knowledge_text, constraints
