#Code for converting bitod format data to risawoz, weather domain
#Giulianna Hashemi-Asasi

import string
import io
import time 
import json

# t = time.time()
name = "bitod/db/exported/zh/weathers.jsonl"
list_of_lines = []
with open(name) as infile:
    for line in infile:
        list_of_lines.append(json.loads(line))

    output = []
    for line_num in range(len(list_of_lines)):
        d = list_of_lines[line_num]
        risawoz_d = {
            "city": None,
            "date": None,
            "weather_condition": None,
            "temperature": None,
            "wind": None,
            "UV_intensity": None
            }
        #Assign key-value pairs from bitod
      #  set key in risawoz_d to value of bitod equiv key
        risawoz_d['city'] = d['city']
        risawoz_d['date'] = d['day']
        risawoz_d['weather_condition'] = d['weather']
        risawoz_d['temperature'] = "minimum temperature: "+str(d['min_temp'])+ " and maximum temperature: " + str(d['max_temp'])

        # print(d)
        # print(risawoz_d)
        output.append(risawoz_d)
    print(output)
    print(len(output))
with open('weathers_risawoz_file.jsonl', 'w+') as outfile:
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
# BITOD SLOTS (6): {"_id","max_temp","min_temp","day","city","weather"}



# RISAWOZ SLOTS (6):
# {
#     "city": None,
#     "date": None,
#     "weather_condition": None,
#     "temperature": None,
#     "wind": None,
#     "UV_intensity": None
#   }
#overlap slots for hotels: city, date/day, weather_condition/weather, temperature/min_temp AND max_temp
#blank risawoz to leave: wind, UV_intensity





