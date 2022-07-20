def call_api(db, api_names, constraints, lang, value_mapping, actions=None):
    knowledge = {}
    for api in api_names:
        if api not in constraints:
            continue
        knowledge[api] = {}
        domain_constraints = constraints[api]
        db_name = f'{value_mapping.zh2en_DOMAIN_MAP.get(api, api)}_{lang}'
        cursor = db[db_name].find(domain_constraints)
        domain_knowledge = []
        for matched in cursor:
            matched["_id"] = str(matched["_id"])
            domain_knowledge.append(matched)
        if domain_knowledge:
            if actions:
                acts = actions[api]
                for item in domain_knowledge:
                    found = True
                    for slot, value in acts.items():
                        slot = slot.replace('.', '\uFF0E')
                        slot = slot.replace('_', ' ')
                        if slot not in item:
                            if slot == '价格' and api == '汽车':
                                slot = '价格(万元)'
                            if slot == '老师' and api == '辅导班':
                                slot = '教师'
                            if slot == '开放时间' and api == '餐厅':
                                slot = '营业时间'
                            if slot == '出发时间' and api == '飞机':
                                slot = '起飞时间'
                        if slot not in item:
                            print(slot)
                        if item[slot] not in value:
                            found = False
                    if found:
                        knowledge[api] = item
                        break

            # if failed return first result
            # keep only the first result
            if not knowledge[api]:
                knowledge[api] = domain_knowledge[0]

            knowledge[api]["available_options"] = len(domain_knowledge)
    return knowledge
