import re


def replace_word(input, search, replace):
    def replace_method(match):
        if match.group(2) is None:
            return match.group()
        return match.group(2).replace(search, replace)

    expr = re.compile("('[^']*'|\"[^\"]*\")|({})".format(search))
    return re.sub(expr, replace_method, input)


s = "( movie ) production_country_or_area 年代 equal_to \" 年代中国大陆 \" , 年代 equal_to \" 2010 年代 \" 年代 production_country_or_area 年代 equal_to \" 年代中国大陆 \" ,"
output = replace_word(s, "年代", "decade")
print(output)
