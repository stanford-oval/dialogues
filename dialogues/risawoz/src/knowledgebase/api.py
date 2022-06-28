def call_api(db, api_names, constraints, lang, value_mapping):
    knowledge = {}
    for api in api_names:
        if api not in constraints:
            continue
        knowledge[api] = {}
        domain_constraints = constraints[api]
        domain_constraints = {value_mapping.en2zh_SLOT_MAP[k]: v for k, v in domain_constraints.items()}
        db_name = f'{value_mapping.zh2en_DOMAIN_MAP.get(api, api)}_{lang}'
        cursor = db[db_name].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            matched["_id"] = str(matched["_id"])
            domain_knowledge.append(matched)
        if domain_knowledge:
            # keep only the first result
            knowledge[api] = domain_knowledge[0]
            knowledge[api]["可用选项"] = len(domain_knowledge)
    return knowledge
