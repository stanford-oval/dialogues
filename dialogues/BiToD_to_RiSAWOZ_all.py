#Code for converting bitod format data to risawoz, attractions domain
#Giulianna Hashemi-Asasi

import string
import io
import time 
import json
import argparse

# command line input
parser = argparse.ArgumentParser()
parser.add_argument("path", help="enter the file path")
args = parser.parse_args()
print("Argument Path Entered: ")
print(args.path)


name = args.path
list_of_lines = []
with open(name) as infile:
    for line in infile:
        list_of_lines.append(json.loads(line))
    output = []
    # ATTRACTIONS CASE
    if name == "bitod/db/exported/zh/attractions.jsonl":
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

            output.append(risawoz_d)
        print(output)
        print(len(output))
        with open('attractions_risawoz_file.jsonl', 'w+') as outfile:
            for ind in range(len(output)):
                if ind == 0:
                    outfile.write(json.dumps(output[ind], indent = 4, ensure_ascii=False))
                else:
                    outfile.write(',\n' + json.dumps(output[ind], indent = 4, ensure_ascii=False))

    elif name == "bitod/db/exported/zh/hotels.jsonl":
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
    elif name == "bitod/db/exported/zh/restaurants.jsonl":
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
    elif name == "bitod/db/exported/zh/weathers.jsonl":
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
            output.append(risawoz_d)
        print(output)
        print(len(output))
        with open('weathers_risawoz_file.jsonl', 'w+') as outfile:
            for ind in range(len(output)):
                if ind == 0:
                    outfile.write(json.dumps(output[ind], indent = 4, ensure_ascii=False))
                else:
                    outfile.write(',\n' + json.dumps(output[ind], indent = 4, ensure_ascii=False))









# Setup: 
# 1) have this file in folder = dialogues/dialogues 
# 2) None value temporarily fills missing slots 


