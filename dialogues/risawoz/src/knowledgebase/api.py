from pymongo import MongoClient

from dialogues.risawoz.src.knowledgebase.en_zh_mappings import RisaWOZMapping

mongodb_host = 'mongodb+srv://bitod:plGYPp44hASzGbmm@cluster0.vo7pq.mongodb.net/bilingual_tod?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE'
client = MongoClient(mongodb_host, authSource='admin')

# risawoz db collections are under bilingual_tod; fix once we get around permission errors
risawoz_db = client["bilingual_tod"]
# for col in risawoz_db.list_collection_names():
#     if '_risawoz' in col:
#         risawoz_db.drop_collection(col)
risawoz_mapping = RisaWOZMapping()


def call_api(api_names, constraints=None, lang=None):
    knowledge = {}
    for api in api_names:
        if api not in constraints:
            continue
        knowledge[api] = {}
        domain_constraints = constraints[api]
        # db_name = api if api_map is None else api_map[api]
        db_name = f'{risawoz_mapping._risawoz_API_MAP[api]}_{lang}_risawoz'
        # cursor = db[api].find(domain_constraints).sort([("rating", pymongo.ASCENDING), ("_id", pymongo.DESCENDING)])
        cursor = risawoz_db[db_name].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            matched["_id"] = str(matched["_id"])
            domain_knowledge.append(matched)
        if domain_knowledge:
            # keep only the first result
            knowledge[api] = domain_knowledge[0]
            knowledge[api]["可用选项"] = len(domain_knowledge)
    return knowledge
