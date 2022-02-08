import json
import os
import re
from typing import Any, Dict, List, Text, Tuple

import pymongo
from pymongo import MongoClient

from ...src.knowledgebase.en_zh_mappings import en2zh_SLOT_MAP, en_zh_API_MAP, entity_map, zh2en_API_MAP, zh2en_SLOT_MAP
from .hk_mtr import MTR

# mongodb_host = os.getenv('BITOD_MONGODB_HOST')
mongodb_host = 'mongodb+srv://bitod:plGYPp44hASzGbmm@cluster0.vo7pq.mongodb.net/bilingual_tod?retryWrites=true&w=majority'

if mongodb_host:
    client = MongoClient(mongodb_host, authSource='admin')
else:
    client = MongoClient(authSource='admin')

mydb = client["bilingual_tod"]
list(mydb.list_collections())
db = mydb["hotels_en_US"]
list(db.find({}))


def is_equal_to(value):
    if is_mongo:
        return value  #
    else:
        return lambda x: x == value


def is_not(value):
    if is_mongo:
        return {"$ne": value}  #
    else:
        # return lambda x: x == value
        return lambda x: x != value


def contains_none_of(value):
    if is_mongo:
        return {"$nin": value}  #
    else:
        return lambda x: not any([e in x for e in value])


def is_one_of(value):
    if is_mongo:
        return {"$in": value}  #
    else:
        return lambda x: x in value


def is_at_least(value):
    if is_mongo:
        return {"$gte": value}  #
    else:
        return lambda x: x >= value


def is_less_than(value):
    if is_mongo:
        return {"$lt": value}  #
    else:
        return lambda x: x < value


def is_at_most(value):
    if is_mongo:
        return {"$lte": value}  #
    else:
        return lambda x: x <= value


def contain_all_of(value):
    return lambda x: all([e in x for e in value])


def contain_at_least_one_of(value):
    return lambda x: any([e in x for e in value])


dbs = {"null": None}

for domain in ['restaurants', 'hotels']:
    for lang in ['en_US', 'zh_CN', 'fa_IR']:
        dbs[f"{domain}_{lang}_booking"] = mydb[f"{domain}_{lang}"]
        dbs[f"{domain}_{lang}_search"] = mydb[f"{domain}_{lang}"]

for domain in ['attractions', 'weathers']:
    for lang in ['en_US', 'zh_CN', 'fa_IR']:
        dbs[f"{domain}_{lang}_search"] = mydb[f"{domain}_{lang}"]

is_mongo = True


def constraint_and(constraint1, constraint2):
    return lambda x: constraint1(x) and constraint2(x)


def constraint_list_to_dict(constraints: List[Dict[Text, Any]]) -> Dict[Text, Any]:
    result = {}
    for constraint in constraints:
        for name, constraint_function in constraint.items():
            # print(name, callable(constraint_function))
            if name not in result:
                result[name] = constraint_function
            else:
                result[name] = constraint_and(result[name], constraint_function)
    return result


def restaurants_en_US_booking(db, query, api_out_list=None, lang=None):
    pre_api_return = {"user_name": query["user_name"], "number_of_people": query["number_of_people"], "time": query["time"]}
    api_out_list.remove("number_of_people")
    api_out_list.remove("time")
    api_out_list.remove("date")
    if "date" in query:
        pre_api_return["date"] = query["date"]
        del query["date"]
    del query["user_name"]
    query["max_num_people_book"] = {"$gte": query["number_of_people"]}
    del query["number_of_people"]

    # print("before: {}".format(query["time"]))
    temp = int(query["time"].split(":")[0])
    temp %= 12
    if "pm" in query["time"]:
        temp += 12
    mins = float(re.findall(r"[0-9][0-9]", query["time"].split(":")[1])[0]) / 60
    temp += mins
    # print(f"after: {temp}")
    query["time"] = temp
    query["open_time"] = {"$lte": query["time"]}
    query["close_time"] = {"$gte": query["time"]}
    del query["time"]
    res = list(db.find(query))

    results = []
    for r in res:
        r["_id"] = str(r["_id"])
        results.append(r)

    if len(results) == 0:

        return (
            dict(
                Message="Sorry, the restaurant is not available given the booking time and number of people. The booking is failed."
            ),
            len(results),
            query,
        )
    else:
        api_return = {k: results[-1][k] for k in api_out_list}
        api_return.update(pre_api_return)
        return api_return, len(results), query


def restaurants_zh_CN_booking(db, query, api_out_list=None):
    pre_api_return = {
        "user_name": query["user_name"],
        "number_of_people": query["number_of_people"],
        "time": query["time"],
        "date": query["date"],
    }
    api_out_list.remove("number_of_people")
    api_out_list.remove("time")
    api_out_list.remove("date")
    del query["date"]
    del query["user_name"]
    query["max_num_people_book"] = {"$gte": query["number_of_people"]}
    del query["number_of_people"]

    if "上午" in query["time"]:
        temp = query["time"].replace("上午", "")

    if "下午" in query["time"]:
        temp = query["time"].replace("下午", "")

    temp, m = temp.split(":")
    temp = int(temp)
    m = float(m)

    temp %= 12
    if "下午" in query["time"]:
        temp += 12

    mins = m / 60
    temp += mins
    # print(f"after: {temp}")
    query["time"] = temp
    query["open_time"] = {"$lte": query["time"]}
    query["close_time"] = {"$gte": query["time"]}
    del query["time"]
    res = list(db.find(query))

    results = []
    for r in res:
        r["_id"] = str(r["_id"])
        results.append(r)

    if len(results) == 0:
        return dict(Message="对不起，预约失败。"), len(results), query
    else:
        api_return = {k: results[-1][k] for k in api_out_list}
        api_return.update(pre_api_return)
        api_return = {en2zh_SLOT_MAP[k]: v for k, v in api_return.items()}
        return api_return, len(results), query


def hotels_en_US_booking(db, query, api_out_list=None):
    pre_api_return = {
        "user_name": query["user_name"],
        "number_of_rooms": query["number_of_rooms"],
        "start_month": query["start_month"],
        "start_day": query["start_day"],
        "number_of_nights": query["number_of_nights"],
    }
    api_out_list.remove("number_of_rooms")
    del query["user_name"]
    query["num_of_rooms"] = {"$gte": query["number_of_rooms"]}
    del query["number_of_rooms"]
    del query["start_month"]
    del query["start_day"]
    del query["number_of_nights"]

    res = list(db.find(query))

    results = []
    for r in res:
        r["_id"] = str(r["_id"])
        results.append(r)

    if len(results) == 0:

        return (
            dict(Message="Sorry, the hotel is not available given the number of rooms. The booking is failed."),
            len(results),
            query,
        )
    else:
        api_return = {k: results[-1][k] for k in api_out_list}
        api_return.update(pre_api_return)
        return api_return, len(results), query


def hotels_zh_CN_booking(db, query, api_out_list=None):
    pre_api_return = {
        "user_name": query["user_name"],
        "number_of_rooms": query["number_of_rooms"],
        "start_month": query["start_month"],
        "start_day": query["start_day"],
        "number_of_nights": query["number_of_nights"],
    }
    api_out_list.remove("number_of_rooms")
    del query["user_name"]
    query["num_of_rooms"] = {"$gte": query["number_of_rooms"]}
    del query["number_of_rooms"]
    del query["start_month"]
    del query["start_day"]
    del query["number_of_nights"]

    res = list(db.find(query))

    results = []
    for r in res:
        r["_id"] = str(r["_id"])
        results.append(r)

    if len(results) == 0:

        return dict(Message="对不起，预约失败。"), len(results), query
    else:
        api_return = {k: results[-1][k] for k in api_out_list}
        api_return.update(pre_api_return)
        api_return = {en2zh_SLOT_MAP[k]: v for k, v in api_return.items()}
        return api_return, len(results), query


def general_search_en_US(db, query, api_out_list=None):
    res = list(db.find(query).sort([("rating", pymongo.ASCENDING), ("_id", pymongo.DESCENDING)]))
    results = []
    for r in res:
        r["_id"] = str(r["_id"])
        results.append(r)
    if len(results) == 0:
        return {}, len(results), query
    else:
        # print(res)
        api_return = {k: results[-1][k] for k in api_out_list}
        api_return["available_options"] = len(results)

        if "price_per_night" in api_return:
            api_return["price_per_night"] = str(api_return["price_per_night"]) + " HKD"
        return api_return, len(results), query


def general_search_zh_CN(db, query, api_out_list=None):
    res = list(db.find(query).sort([("rating", pymongo.ASCENDING), ("_id", pymongo.DESCENDING)]))
    results = []
    for r in res:
        r["_id"] = str(r["_id"])
        results.append(r)
    if len(results) == 0:
        return {}, len(results), query
    else:
        # print(res)
        api_return = {k: results[-1][k] for k in api_out_list}
        api_return["available_options"] = len(results)

        if "price_per_night" in api_return:
            api_return["price_per_night"] = str(api_return["price_per_night"]) + "港币"
        api_return = {en2zh_SLOT_MAP[k]: v for k, v in api_return.items()}
        return api_return, len(results), query


def query_mongo(api_name, db, query, api_out_list=None, lang=None):
    if api_name == "restaurants_en_US_booking":
        res, count, query = restaurants_en_US_booking(db, query, api_out_list, lang)
    elif api_name == "hotels_en_US_booking":
        res, count, query = hotels_en_US_booking(db, query, api_out_list)
    elif api_name == "restaurants_zh_CN_booking":
        res, count, query = restaurants_zh_CN_booking(db, query, api_out_list)
    elif api_name == "hotels_zh_CN_booking":
        res, count, query = hotels_zh_CN_booking(db, query, api_out_list)
    elif "zh" in api_name:
        res, count, query = general_search_zh_CN(db, query, api_out_list)
    else:
        res, count, query = general_search_en_US(db, query, api_out_list)
    return res, count, query


def call_api(api_name, constraints: List[Dict[Text, Any]], lang=None) -> Tuple[Dict[Text, Any], int, dict]:
    global is_mongo

    # Canonicalization
    for slot, value in constraints[0].items():
        if isinstance(value, str) and (value in entity_map):
            constraints[0][slot] = entity_map[value]
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, str) and (v in entity_map):
                    constraints[0][slot][k] = entity_map[v]
                if isinstance(v, list):
                    constraints[0][slot][k] = [entity_map[v_v] if v_v in entity_map else v_v for v_v in v]

    if api_name in [
        "restaurants_en_US_search",
        "restaurants_en_US_booking",
        "hotels_en_US_search",
        "hotels_en_US_booking",
        "attractions_en_US_search",
        "weathers_en_US_search",
        "餐馆查询",
        "餐馆预订",
        "宾馆查询",
        "宾馆预订",
        "景点查询",
        "天气查询",
    ]:

        if 'zh' in lang:
            api_name = en_zh_API_MAP.get(api_name, api_name)

        api_name = zh2en_API_MAP.get(api_name, api_name)
        constraints = [{zh2en_SLOT_MAP.get(k, k): v for k, v in constraints[0].items()}]

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "apis", api_name + ".json"), "r") as file:
            api_schema = json.load(file)
        is_mongo = True
        if constraints:
            all_provided_parameters = set.union(*[set(c) for c in constraints])
        else:
            all_provided_parameters = set()

        for parameter in api_schema["required"]:
            if parameter not in all_provided_parameters:
                raise ValueError(f"Parameter '{parameter}' is required but was not provided.")

        api_out_list = [slot["Name"] for slot in api_schema["output"]]

        if lang:
            if 'en' in lang:
                lang = 'en_US'
            db = dbs[re.sub(re.compile('(\w+_)\w{2}_\w{2}(_\w+)'), fr'\1{lang}\2', api_name)]
        else:
            db = dbs[api_name]

        res, count, query = query_mongo(api_name, db, constraint_list_to_dict(constraints), api_out_list, lang)
        # res, count = query_mongo(dbs[api_name], constraints)
        return res, count, query

    elif api_name in ["HKMTR_en", "HKMTR_zh", "香港地铁"]:

        if api_name == 'HKMTR_zh':
            api_name = '香港地铁'

        api_name = zh2en_API_MAP.get(api_name, api_name)
        constraints = [{zh2en_SLOT_MAP.get(k, k): v for k, v in constraints[0].items()}]
        # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "apis", api_name + ".json"), "r") as file:
        #     api_schema = json.load(file)

        source = constraint_list_to_dict(constraints)["departure"]
        target = constraint_list_to_dict(constraints)["destination"]
        if not lang:
            lang = api_name.split("_")[1]
        try:
            lang = lang[:2]
            mtr_dict = MTR(source=source, target=target, lang=lang)
        except Exception:
            return None, -1, None

        return mtr_dict, 1, None
    else:
        raise ValueError(f"API'{api_name}' is not available.")
