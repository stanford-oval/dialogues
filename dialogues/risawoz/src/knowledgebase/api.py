import pymongo


def call_api(api_name, mongodb_host, constraints=None, api_map=None):
    # api name equals to domain name
    knowledge = {}
    num_matched = 0
    db = pymongo.MongoClient(mongodb_host)["risawoz_database"]
    for api in api_name:
        domain_constraints = constraints[api]
        api = api if api_map is None else api_map[api]
        # cursor = db[api].find(domain_constraints).sort([("rating", pymongo.ASCENDING), ("_id", pymongo.DESCENDING)])
        cursor = db[api].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            matched["_id"] = str(matched["_id"])
            domain_knowledge.append(matched)
        if domain_knowledge:
            knowledge[api] = domain_knowledge[0]
            knowledge[api]["可用选项"] = len(domain_knowledge)
            num_matched += len(domain_knowledge)
    return knowledge, num_matched
