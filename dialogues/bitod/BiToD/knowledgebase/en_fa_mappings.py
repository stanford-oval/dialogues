fa2en_CARDINAL_MAP = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
}
en2fa_CARDINAL_MAP = {v: k for k, v in fa2en_CARDINAL_MAP.items()}


en2fa_ACT_MAP = {
    'inform': 'اطلاع_دادن',
    'inform_intent': 'قصد_اطلاع_رسانی',
    'confirm': 'تایید',
    'offer': 'پیشنهاد',
    'request': 'درخواست',
    "request_more": "درخواست_بیشتر",
    "greeting": "تبریک",
    "thank_you": "متشکرم",
    "affirm": "تأیید_کردن",
    "negate": "نفی",
    "notify_success": "اطلاع_از_موفقیت",
    "notify_fail": "اطلاع_از_شکست",
    "goodbye": "خداحافظ",
    "request_update": "درخواست_به_روز_رسانی",
}
fa2en_ACT_MAP = {v: k for k, v in en2fa_ACT_MAP.items()}


en2fa_INTENT_MAP = {
    'inform': 'اطلاع_دادن',
    'confirm': 'تایید',
    'offer': 'پیشنهاد',
    'request': 'درخواست',
    "request_more": "درخواست_بیشتر",
    "greeting": "تبریک",
    "affirm": "تأیید_کردن",
    "notify_success": "اطلاع_از_موفقیت",
    "notify_fail": "اطلاع_از_شکست",
    "goodbye": "خداحافظ",
    "request_update": "درخواست_به_روز_رسانی",
}
fa2en_INTENT_MAP = {v: k for k, v in en2fa_INTENT_MAP.items()}

en2fa_SLOT_MAP = {
    "intent": "قصد",
    "name": "نام",
    "location": "محل",
    "rating": "رتبه_بندی",
    "type": "نوع",
    "address": "نشانی",
    "phone_number": "شماره_تلفن",
    "available_options": "گزینه_های_موجود",
    "ref_number": "شماره_مرجع",
    "price_per_night": "قیمت_شب",
    "user_name": "نام_کاربری",
    "number_of_rooms": "تعداد_اتاق_ها",
    "start_month": "شروع_ماه",
    "start_day": "روز_شروع",
    "start_date": "تاریخ_شروع",
    "number_of_nights": "تعداد_شبها",
    "price_level": "سطح_قیمت",
    "stars": "ستاره_ها",
    "cuisine": "غذا",
    "dietary_restrictions": "محدودیت_های_غذایی",
    "day": "روز",
    "city": "شهر",
    "max_temp": "حداکثر_دما",
    "min_temp": "دقیقه_دما",
    "weather": "آب_و_هوا",
    "description": "شرح",
    "departure": "عزیمت،_خروج",
    "destination": "مقصد",
    "number_of_people": "تعداد_مردم",
    "time": "زمان",
    "date": "تاریخ",
    "estimated_time": "زمان_تخمین_زده_شده",
    "shortest_path": "کوتاهترین_راه",
    "price": "قیمت",
}

fa2en_SLOT_MAP = {v: k for k, v in en2fa_SLOT_MAP.items()}


en2fa_RELATION_MAP = {"equal_to": "برابر", "not": "نابرابر", "less_than": "کمتر_از", "at_least": "حداقل", "one_of": "یکی_از"}
fa2en_RELATION_MAP = {v: k for k, v in en2fa_RELATION_MAP.items()}

fa2en_SPECIAL_MAP = {"بی_اهمیت": "don't care"}
en2fa_SPECIAL_MAP = {v: k for k, v in fa2en_SPECIAL_MAP.items()}


fa2en_API_MAP = {
    "جستجوی_رستوران": "restaurants_fa_XX_search",
    "رزرو_رستوران": "restaurants_fa_XX_booking",
    "جستجوی_هتل": "hotels_fa_XX_search",
    "رزرو_هتل": "hotels_fa_XX_booking",
    "جستجوی_جاذبه_ها": "attractions_fa_XX_search",
    "وضعیت_آب_و_هوا": "weathers_fa_XX_search",
    "مترو_هنگ_کنگ": "HKMTR_fa",
}
en2fa_API_MAP = {v: k for k, v in fa2en_API_MAP.items()}


# Mapping between api file names in kb/apis/* to a canonical name
fa2en_DOMAIN_MAP = {
    "جستجوی_رستوران": "restaurants search",
    "رزرو_رستوران": "restaurants booking",
    "جستجوی_هتل": "hotels search",
    "رزرو_هتل": "hotels booking",
    "جستجوی_جاذبه_ها": "attractions search",
    "وضعیت_آب_و_هوا": "weathers search",
    "مترو_هنگ_کنگ": "HKMTR en",
}
en2fa_DOMAIN_MAP = {v: k for k, v in fa2en_DOMAIN_MAP.items()}


en_API_MAP = {
    'chat': 'chat',
    "restaurants_en_US_search": "restaurants search",
    "restaurants_en_US_booking": "restaurants booking",
    "hotels_en_US_search": "hotels search",
    "hotels_en_US_booking": "hotels booking",
    "attractions_en_US_search": "attractions search",
    "weathers_en_US_search": "weathers search",
    "HKMTR_en": "HKMTR en",
}

fa_en_API_MAP = {
    "جستجوی_رستوران": "restaurants_en_US_search",
    "رزرو_رستوران": "restaurants_en_US_booking",
    "جستجوی_هتل": "hotels_en_US_search",
    "رزرو_هتل": "hotels_en_US_booking",
    "جستجوی_جاذبه_ها": "attractions_en_US_search",
    "وضعیت_آب_و_هوا": "weathers_en_US_search",
    "مترو_هنگ_کنگ": "HKMTR_en",
}
API_MAP = {}
API_MAP.update(en_API_MAP)
API_MAP.update(en2fa_API_MAP)
API_MAP.update({k: k for k, v in fa2en_API_MAP.items()})


# for cross lingual transfer
# mapping between slot values, not comprehensive, don't rely on it
# cur_dir = os.path.dirname(os.path.abspath(__file__))
# with open(os.path.join(cur_dir, "mappings/dict_en_fa.json")) as f:
#     en2fa_VALUE_MAP = json.load(f)
# fa2en_VALUE_MAP = {v: k for k, v in en2fa_VALUE_MAP.items()}


# maps entities to their canonicalized version; api expects canonicalized version
# note entities in original and preprocessed datasets are not canonicalized;
# cur_dir = os.path.dirname(os.path.abspath(__file__))
# entity_map = {}
# with open(os.path.join(cur_dir, "mappings/zh_entity_map.json")) as f:
#     entity_map.update(json.load(f))
# with open(os.path.join(cur_dir, "mappings/en_entity_map.json")) as f:
#     entity_map.update(json.load(f))
#
# reverse_entity_map = {v: k for k, v in entity_map.items()}
