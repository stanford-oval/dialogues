#Code for converting bitod format data to risawoz, hotels domain
#Giulianna Hashemi-Asasi

import string
import io
import time 
import json
import argparse

# t = time.time()
name = "bitod/db/exported/zh/hotels.jsonl"
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
            "star": None,
            "pricerange": None,
            "hotel_type": None,
            "room_type": None,
            "parking": None,
            "room_charge": None,
            "address": None,
            "phone_number": None,
            "score": None
            }
        #Assign key-value pairs from bitod
      #  set key in risawoz_d to value of bitod equiv key
        risawoz_d['name'] = d['name']
        risawoz_d['area'] = d['location']
        risawoz_d['star'] = d['stars']
        risawoz_d['pricerange'] = d['price_level']
        risawoz_d['room_charge'] = d['price_per_night']
        risawoz_d['phone_number'] = d['phone_number']
        risawoz_d['score'] = d['rating']
        # print(d)
        # print(risawoz_d)
        output.append(risawoz_d)
    print(output)
    print(len(output))
    with open('hotels_risawoz_file.jsonl', 'w+') as outfile:
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
# BITOD SLOTS (13): "_id","stars","name", "price_level","price_per_night","rating","latitude","longitude","photo","location","ref_number","phone_number","num_of_rooms"

# RISAWOZ SLOTS (11):
# {
#     "name": ,
#     "area": ,
#     "star":,
#     "pricerange": ,
#     "hotel_type": ,
#     "room_type": ,
#     "parking": ,
#     "room_charge": ,
#     "address": ,
#     "phone_number": ,
#     "score":
#   },
#overlap slots for hotels: name, area/location, star/stars, pricerange/price_level, room_charge/price_per_night, phone_number, score/rating
#blank risawoz to leave: hotel_type, room_type, parking, address







