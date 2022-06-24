from pymongo import MongoClient

from dialogues.risawoz.src.knowledgebase.en_zh_mappings import RisawozMapping

mongodb_host = 'mongodb+srv://bitod:plGYPp44hASzGbmm@cluster0.vo7pq.mongodb.net/risawoz?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE'
client = MongoClient(mongodb_host, authSource='admin')

risawoz_db = client["risawoz"]
risawoz_mapping = RisawozMapping()


def call_api(api_names, constraints=None, mongodb_host=None, lang=None):
    global risawoz_db
    if mongodb_host:
        client = MongoClient(mongodb_host, authSource='admin')
        risawoz_db = client["risawoz"]

    knowledge = {}
    for api in api_names:
        if api not in constraints:
            continue
        knowledge[api] = {}
        domain_constraints = constraints[api]
        db_name = f'{risawoz_mapping.zh2en_DOMAIN_MAP[api]}_{lang}'
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
