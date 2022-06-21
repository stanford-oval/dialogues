import os

import pymongo
from bitod.src.knowledgebase.en_zh_mappings import en_zh_API_MAP
from risawoz.src.convert import build_db

cur_dir = os.path.dirname(os.path.abspath(__file__))
build_db(
    db_json_path=os.path.join(*[cur_dir, '../db', 'zh']), api_map=en_zh_API_MAP, mongodb_host="mongodb://localhost:27017/"
)


def call_api(api_name, mongodb_host, constraints=None, api_map=None):
    # api name equals to domain name
    knowledge = {}
    db = pymongo.MongoClient(mongodb_host)["risawoz_database"]
    for api in api_name:
        if api not in constraints:
            continue
        knowledge[api] = {}
        domain_constraints = constraints[api]
        api = api if api_map is None else api_map[api]
        # cursor = db[api].find(domain_constraints).sort([("rating", pymongo.ASCENDING), ("_id", pymongo.DESCENDING)])
        cursor = db[api].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            matched["_id"] = str(matched["_id"])
            domain_knowledge.append(matched)
        if domain_knowledge:
            # keep only the first result
            knowledge[api] = domain_knowledge[0]
            knowledge[api]["可用选项"] = len(domain_knowledge)
    return knowledge
