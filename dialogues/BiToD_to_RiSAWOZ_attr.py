#Code for converting bitod format data to risawoz, attractions domain
#Giulianna Hashemi-Asasi

import string
import io
import time 
import json

t = time.time()
name = "bitod/db/exported/zh/attractions.jsonl"
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
            "attraction_type": None,
            "best_for_the_crowd": None,
            "consumption": None,
            "whether_the_subway_goes_directly": None,
            "ticket_price": None,
            "phone_number": None,
            "address": None,
            "rating": None,
            "open_hours": None,
            "features": None
        }
        #Assign key-value pairs from bitod
      #  set key in risawoz_d to value of bitod equiv key
        risawoz_d['name'] = d['name']
        risawoz_d['area'] = d['location']
        risawoz_d['attraction_type'] = d['type']
        risawoz_d['phone_number'] = d['phone_number']
        risawoz_d['address'] = d['address']
        risawoz_d['rating'] = d['rating']
        risawoz_d['features'] = d['description']
        # print(d)
        # print(risawoz_d)
        output.append(risawoz_d)
    print(output)
    print(len(output))
with open('attractions_risawoz_file.jsonl', 'w+') as outfile:
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
# BITOD SLOTS (11): id, description, latitude, longitude, rating, phone_number, address, name, location, type, photo
# RISAWOZ SLOTS (12):
    # "name",
    # "area",
    # "attraction_type",
    # "best_for_the_crowd",
    # "consumption",
    # "whether_the_subway_goes_directly",
    # "ticket_price",
    # "phone_number",
    # "address",
    # "rating",
    # "open_hours",
    # "features"
#overlap slots for attractions: rating, phone number, address, name, type/attraction_type, location/area, description/features
#blank risawoz to leave: crowd, consumption, subway, ticket, hours







