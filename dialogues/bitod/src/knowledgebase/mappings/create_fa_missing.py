import string
import json

# t = time.time()
name = "en2zh_missing.json"
name2 = "missing_fa_only.json"
# with open(name2) as farsi_values:
#     farsi_dct = json.load(farsi_values)
#     for key in farsi_dct:
#         print(key)
#Printing keys
with open(name) as infile:
    dct = json.load(infile)
#     for key in dct:
#         print(key)
lst_of_farsi = []
with open(name2) as farsi_values:
    for line in farsi_values:
        line = line.strip('\n')
        # line = line.strip('\"')
        lst_of_farsi.append(line)
    print(lst_of_farsi)
    #assign dct values to be lines of farsi_values
    line_num = 1
    for key in dct:
        dct[key] = lst_of_farsi[line_num]
        line_num += 1


with open('en2fa_missing', 'w+') as outfile:
    outfile.write(json.dumps(dct, indent = 4, ensure_ascii=False))
