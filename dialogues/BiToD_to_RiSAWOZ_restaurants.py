#Code for converting bitod format data to risawoz, restaurants domain
#Giulianna Hashemi-Asasi

import string
import io
import time 
import json

# t = time.time()
name = "bitod/db/exported/zh/restaurants.jsonl"
list_of_lines = []
with open(name) as infile:
    for line in infile:
        list_of_lines.append(json.loads(line))

    output = []
    for line_num in range(len(list_of_lines)):
        d = list_of_lines[line_num]
        risawoz_d = {
            "name": None,
            "area": None,
            "cuisine": None,
            "pricerange": None,
            "metro_station": None,
            "per_capita_consumption": None,
            "address": None,
            "phone_number": None,
            "score": None,
            "business_hours": None,
            "dishes": None
            }
        #Assign key-value pairs from bitod
      #  set key in risawoz_d to value of bitod equiv key
        risawoz_d['name'] = d['name']
        risawoz_d['area'] = d['location']
        risawoz_d['cuisine'] = d['cuisine']
        risawoz_d['pricerange'] = d['price_level']
        risawoz_d['address'] = d['address']
        risawoz_d['phone_number'] = d['phone_number']
        risawoz_d['score'] = d['rating']
        risawoz_d['business_hours'] = str(d['open_time'])+ " to " + str(d['close_time'])
        risawoz_d['dishes'] = d['description']

        # print(d)
        # print(risawoz_d)
        output.append(risawoz_d)
    print(output)
    print(len(output))
with open('restaurants_risawoz_file.jsonl', 'w+') as outfile:
    for ind in range(len(output)):
        if ind == 0:
            outfile.write(json.dumps(output[ind], indent = 4, ensure_ascii=False))
        else:
            outfile.write(',\n' + json.dumps(output[ind], indent = 4, ensure_ascii=False))

    # json.dump(output, outfile)


# elapsed = time.time() - t
# print(elapsed)

# Setup/ideas: 
# 1) have this file in folder = dialogues/dialogues 
# 2) for loop iterate through Bitod files in bitod/db/exported/zh (one algorithn for each, keep apart)
# attractions.jsonl, hotels.jsonl, restaurants.jsonl, weathers.jsonl
# 3) read line by line 
# put a None value for missing slots 
# Attractions:
# BITOD SLOTS (17): {"_id":,"name":,"address":,"phone_number":,"description":,"price_level":,"rating":,"cuisine":,"dietary_restrictions":,"latitude":,"longitude":,"photo","location":,"open_time":,"close_time":,"max_num_people_book":,"ref_number":}


# RISAWOZ SLOTS (11):
# {
#     "name": None,
#     "area": None,
#     "cuisine": None,
#     "pricerange": None,
#     "metro_station": None,
#     "per_capita_consumption": None,
#     "address": None,
#     "phone_number": None,
#     "score": None,
#     "business_hours": None,
#     "dishes": None
#   }
#overlap slots for hotels: name, area/location, cuisine, pricerange/price_level, address, phone_number, score/rating, business_hours/open_time AND close_time, dishes/description
#blank risawoz to leave: metro_station, per_capita_consumption






