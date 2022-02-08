import json
import os

import networkx as nx
import pydot

cur_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(cur_dir, "mappings/mtr_mapping.json")) as f:
    MTR_map = json.load(f)

graph = pydot.graph_from_dot_file(os.path.join(cur_dir, "mappings/hongkong-mtr_with_eng.dot"))[0]
nx_graph = nx.drawing.nx_pydot.from_pydot(graph)


class key_dict(dict):
    def __getitem__(self, item):
        return item


name_to_en = key_dict()

name_to_fa = {
    "AsiaWorld-Expo": "نمایشگاه آسیای جهانی",
    "Airport": "فرودگاه",
    "Tsing Yi": "سینگ یو",
    "Kowloon": "کولوون",
    "Hong Kong": "هنگ کنگ",
    "Sunny Bay": "خلیج آفتابی",
    "Disneyland Resort": "استر استیشن دیزنی",
    "Diamond Hill": "هیل الماس",
    "Choi Wan": "چای وان",
    "Shun Tin": "شان تین",
    "Sau Mau Ping": "سو ماو پینگ",
    "Po Tat": "پو تات",
    "Po Lam": "پو لام",
    "Tuen Men South": "مردهای تیون جنوبی",
    "Tuen Men": "مردهای تیون",
    "Siu Hong": "سو هونگ",
    "Hung Shui Kiu": "هونگ شوی کیو",
    "Tin Shui Wai": "تین شوی وایی",
    "Long Ping": "لانگ پینگ",
    "Yuen Long": "یوین لانگ",
    "Kam Sheung Road": "جاده کام شونگ",
    "Tsuen Wan West": "تیون وان غربی",
    "Mei Foo": "می فو",
    "Nam Cheong": "نام چنگ",
    "Austin": "آستین",
    "East Tsim Sha Tsui": "شرق تیم شا تی",
    "Hung Hom": "هونگ هوم",
    "Ho Man Tin": "هو مان تین",
    "Ma Tau Wai": "ما تاو وایی",
    "To Kwa Wan": "تو کووا وان",
    "Kai Tak": "کای تاک",
    "Tai Wai": "تای وایی",
    "Che Kung Temple": "معبد چ کونگ",
    "Sha Tin Wai": "شا تین وایی",
    "City One": "شهر اول",
    "Shek Mun": "شیک مان",
    "Tai Shui Hang": "تای شوی هانگ",
    "Heng On": "هنگ آن",
    "Ma On Shan": "ما آن شان",
    "Wu Kai Sha": "و کای شا",
    "Kennedy Town": "شهر کندی",
    "HKU": "هانتون",
    "Sai Ying Pun": "سای ینگ پون",
    "Sheung Wan": "شونگ وان",
    "Central": "مرکزی",
    "Admirality": "Admirality (ادارایی)",
    "Wan Chai": "وان چی",
    "Causeway Bay": "خلیج کاوزウェی",
    "Tin Hau": "تین هاو",
    "Fortress Hill": "تپه قلعه",
    "North Point": "نقطه ی شمالی",
    "Quarry Bay": "خلیج کاوری",
    "Tai Koo": "تای کو",
    "Sai Wan Ho": "سای وان هو",
    "Shau Kei Wan": "شاو کی وان",
    "Heng Fa Chuen": "هنگ فا تشوان",
    "Chai Wan": "چای وان",
    "Whampoa": "ومپوا",
    "Yau Ma Tei": "یا ما تی",
    "Mong Kok": "منگ کوک",
    "Prince Edward": "پرنس ادوارد",
    "Shek Kip Mei": "شیک کیپ می",
    "Kowloon Tong": "کوولون تونگ",
    "Lok Fu": "لوک فو",
    "Wong Tai Sin": "وانگ تای سین",
    "Choi Hung": "چای هونگ",
    "Kowloon Bay": "خلیج کووان",
    "Ngau Tau Kok": "انگтау کوک",
    "Kwun Tong": "کوون تونگ",
    "Lam Tin": "لام تین",
    "Yau Tong": "یا تونگ",
    "Tiu Keng Leng": "تا کینگ لانگ",
    "Kwu Tung": "کو تونگ",
    "Exhibition": "نمایشگاه",
    "Mong Kok East": "منگ کوک شرق",
    "Sha Tin": "شا تین",
    "Fo Tan": "فو تان",
    "Racecourse": "میدان دونده",
    "University": "دانشگاه",
    "Tai Po Market": "بازار تای پو",
    "Tai Wo": "تای وو",
    "Fanling": "فَنَلینگ",
    "Sheung Shui": "شونگ شوی",
    "Lok Ma Chau": "لوک ما Chau",
    "Lo Wu": "لو و",
    "Ocean Park": "پارک اقیانوس",
    "Wong Chuk Hang": "وانگ چوک هانگ",
    "Lei Tung": "لی تونگ",
    "South Horizons": "افقی جنوبی",
    "Queen Mary Hospital": "بیمارستان ملکه مری",
    "Cyberport": "بندر سایبری",
    "Wah Fu": "ووه فو",
    "Tin Wan": "تین وان",
    "Aberdeen": "ابردین",
    "Tamar": "تامار",
    "Victoria Park": "پارک ویکتوریا",
    "Tseung Kwan O": "تسانگ کوان او",
    "Hang Hau": "هانگ هاو",
    "LOHAS Park": "پارک لوها",
    "Tsuen Wan": "تسو آن وان",
    "Tai Wo Hau": "تای و ها",
    "Kwai Hing": "کوای هنگ",
    "Kwai Fong": "کوای فنگ",
    "Lai King": "لای کینگ",
    "Lai Chi Kok": "لای چی کوک",
    "Cheung Sha Wan": "چانگ شا وان",
    "Sham Shui Po": "سام شوی پو",
    "Jordon": "اردن",
    "Tsim Sha Tsui": "تیم شا تی",
    "Tung Chung West": "تونگ چن غربی",
    "Tung Chung": "تونگ چینگ",
    "Tung Chung East": "تونگ چن شرقی",
    "Olympic": "اولمپیک",
    "Ngong Ping": "انگ پینگ",
}

name_to_zh = {
    "AsiaWorld-Expo": "博覽館",
    "Airport": "機場",
    "Tsing Yi": "青衣",
    "Kowloon": "九龍",
    "Hong Kong": "香港",
    "Sunny Bay": "欣澳",
    "Disneyland Resort": "迪士尼",
    "Diamond Hill": "鑽石山",
    "Choi Wan": "彩雲",
    "Shun Tin": "順天",
    "Sau Mau Ping": "秀茂坪",
    "Po Tat": "寶達",
    "Po Lam": "寶琳",
    "Tuen Men South": "屯門南",
    "Tuen Men": "屯門",
    "Siu Hong": "兆康",
    "Hung Shui Kiu": "洪水橋",
    "Tin Shui Wai": "天水圍",
    "Long Ping": "郎屏",
    "Yuen Long": "元郎",
    "Kam Sheung Road": "錦上路",
    "Tsuen Wan West": "荃灣西",
    "Mei Foo": "美孚",
    "Nam Cheong": "南昌",
    "Austin": "柯士甸",
    "East Tsim Sha Tsui": "尖東",
    "Hung Hom": "紅磡",
    "Ho Man Tin": "何文田",
    "Ma Tau Wai": "馬頭圍",
    "To Kwa Wan": "土瓜灣",
    "Kai Tak": "啟德",
    "Tai Wai": "大圍",
    "Che Kung Temple": "車公廟",
    "Sha Tin Wai": "沙田圍",
    "City One": "第一城",
    "Shek Mun": "石門",
    "Tai Shui Hang": "大水坑",
    "Heng On": "恆安",
    "Ma On Shan": "馬鞍山",
    "Wu Kai Sha": "烏溪沙",
    "Kennedy Town": "監尼地城",
    "HKU": "香港大學",
    "Sai Ying Pun": "西營盤",
    "Sheung Wan": "上環",
    "Central": "中環",
    "Admirality": "金鐘",
    "Wan Chai": "灣仔",
    "Causeway Bay": "銅鑼灣",
    "Tin Hau": "天后",
    "Fortress Hill": "炮台山",
    "North Point": "北角",
    "Quarry Bay": "鰂魚涌",
    "Tai Koo": "太古",
    "Sai Wan Ho": "西灣河",
    "Shau Kei Wan": "筲箕灣",
    "Heng Fa Chuen": "杏花邨",
    "Chai Wan": "柴灣",
    "Whampoa": "黃埔",
    "Yau Ma Tei": "油麻地",
    "Mong Kok": "旺角",
    "Prince Edward": "太子",
    "Shek Kip Mei": "石硤尾",
    "Kowloon Tong": "九龍塘",
    "Lok Fu": "樂富",
    "Wong Tai Sin": "黃大仙",
    "Choi Hung": "彩虹",
    "Kowloon Bay": "九龍灣",
    "Ngau Tau Kok": "牛頭角",
    "Kwun Tong": "觀塘",
    "Lam Tin": "藍田",
    "Yau Tong": "油塘",
    "Tiu Keng Leng": "調景嶺",
    "Kwu Tung": "古洞",
    "Exhibition": "會展",
    "Mong Kok East": "旺角東",
    "Sha Tin": "沙田",
    "Fo Tan": "火炭",
    "Racecourse": "馬場",
    "University": "大學",
    "Tai Po Market": "大埔墟",
    "Tai Wo": "太和",
    "Fanling": "粉嶺",
    "Sheung Shui": "上水",
    "Lok Ma Chau": "落馬洲",
    "Lo Wu": "羅湖",
    "Ocean Park": "海洋公園",
    "Wong Chuk Hang": "黃竹坑",
    "Lei Tung": "利東",
    "South Horizons": "海怡半島",
    "Queen Mary Hospital": "瑪麗醫院",
    "Cyberport": "數碼港",
    "Wah Fu": "華富",
    "Tin Wan": "田灣",
    "Aberdeen": "香港仔",
    "Tamar": "添馬",
    "Victoria Park": "維園",
    "Tseung Kwan O": "將軍澳",
    "Hang Hau": "坑口",
    "LOHAS Park": "康城",
    "Tsuen Wan": "荃灣",
    "Tai Wo Hau": "大窩口",
    "Kwai Hing": "葵芳",
    "Kwai Fong": "葵興",
    "Lai King": "荔景",
    "Lai Chi Kok": "荔枝角",
    "Cheung Sha Wan": "長沙灣",
    "Sham Shui Po": "生水埗",
    "Jordon": "佐敦",
    "Tsim Sha Tsui": "尖沙嘴",
    "Tung Chung West": "東涌",
    "Tung Chung": "東涌",
    "Tung Chung East": "東涌",
    "Olympic": "奧運",
    "Ngong Ping": "昂坪",
}

color = {
    "AE": "turquoise",
    "DR": "pink",
    "EK": "tan",
    "EW": "brown",
    "I": "blue",
    "KT": "green",
    "N": "black",
    "NS": "cyan",
    "SIE": "yellowgreen",
    "SIW": "mediumpurple",
    "TKO": "purple",
    "TW": "red",
    "TC": "orange",
    "NP": "orange",
}

color_to_en = key_dict()

color_to_zh = {
    "turquoise": "綠松石",
    "pink": "粉色的",
    "tan": "棕褐色",
    "brown": "棕色的",
    "blue": "藍色",
    "green": "綠色",
    "black": "黑色的",
    "cyan": "青色",
    "yellowgreen": "黃綠色",
    "mediumpurple": "中紫色",
    "purple": "紫色的",
    "red": "紅色的",
    "orange": "橘子",
}

color_to_fa = {
    "turquoise": "فیروزه",
    "pink": "صورتی",
    "tan": "برنزه",
    "brown": "قهوهای",
    "blue": "آبی",
    "green": "سبز",
    "black": "سیاه",
    "cyan": "فیروزهای",
    "yellowgreen": "سبز_زرد",
    "mediumpurple": "بنفش_متوسط",
    "purple": "بنفش",
    "red": "قرمز",
    "orange": "نارنجی",
}


name_line = {
    "AE": "Airport Express Line",
    "DR": "Disneyland Resort Line",
    "EK": "East Kowloon Line",
    "EW": "East West Line",
    "I": "Island Line",
    "KT": "Kwan Tong Line",
    "N": "Northern Line",
    "NS": "North South Line",
    "SIE": "South Island Line (East)",
    "SIW": "South Island Line (West)",
    "TKO": "Tseung Kwan O Line",
    "TW": "Tsuen Wan Line",
    "TC": "Tung Chung Line",
    "NP": "Tung Chung Line",
}

name_missing = {
    "AE1": {"label": "博覽館\rAsiaWorld-Expo"},
    "AE2": {"label": "機場\rAirport"},
    "AE3_TC5": {"label": "青衣\rTsing Yi"},
    "AE5_TC20": {"label": "香港\rHong Kong"},
    "DR1_TC4": {"label": "欣澳\rSunny Bay"},
    "DR2": {"label": "迪士尼\rDisneyland Resort"},
    "I1": {"label": "監尼地城\rKennedy Town"},
    "I2_SIW1": {"label": "香港大學\rHKU"},
    "I3": {"label": "西營盤\rSai Ying Pun"},
    "I4": {"label": "上環\rSheung Wan"},
    "I5_TW16": {"label": "中環\rCentral"},
    "I6_NS1_SIE1_TW15": {"label": "金鐘\rAdmirality"},
    "I7": {"label": "灣仔\rWan Chai"},
    "I8": {"label": "銅鑼灣\rCauseway Bay"},
    "I9": {"label": "天后\rTin Hau"},
    "I10": {"label": "炮台山\rFortress Hill"},
    "I11_TKO4": {"label": "北角\rNorth Point"},
    "I12_TKO5": {"label": "鰂魚涌\rQuarry Bay"},
    "I13": {"label": "西灣河\rSai Wan Ho"},
    "I14": {"label": "筲箕灣\rShau Kei Wan"},
    "I15": {"label": "杏花邨\rHeng Fa Chuen"},
    "I16": {"label": "柴灣\rChai Wan"},
    "SIE2": {"label": "海洋公園\rOcean Park"},
    "SIE3_SIW7": {"label": "黃竹坑\rWong Chuk Hang"},
    "SIE4": {"label": "利東\rLei Tung"},
    "SIE5": {"label": "海怡半島\rSouth Horizons"},
    "SIW2": {"label": "瑪麗醫院\rQueen Mary Hospital"},
    "SIW3": {"label": "數碼港\rCyberport"},
    "SIW4": {"label": "華富\rWah Fu"},
    "SIW5": {"label": "田灣\rTin Wan"},
    "SIW6": {"label": "香港仔\rAberdeen"},
    "TC21_TKO1": {"label": "添馬\rTamar"},
    "NS2_TKO2": {"label": "會展\rExhibition"},
    "TKO3": {"label": "維園\rVictoria Park"},
    "TC1": {"label": "東涌\rTung Chung West"},
    "TC2": {"label": "東涌\rTung Chung"},
    "TC3": {"label": "東涌\rTung Chung East"},
    "NP": {"label": "昂坪\rNgong Ping"},
}

for n in nx_graph.nodes():
    temp = {"name_en": "", "color": [], "line": []}
    if "label" in nx_graph.nodes[n]:
        temp["name_en"] = nx_graph.nodes[n]["label"].split("\\r")[1].replace('"', "")
    else:
        if n in name_missing:
            temp["name_en"] = name_missing[n]["label"].split("\r")[1]
    for id_ in n.split("_"):
        t = [x.isdigit() for x in id_]
        i = len(t)
        if True in t:
            i = [x.isdigit() for x in id_].index(True)
        id_ = id_[:i]

        temp["color"].append(color[id_])
        temp["line"].append(name_line[id_])

    nx_graph.nodes[n].update(temp)


G_MAPS = {'en': nx.Graph(), 'zh': nx.Graph(), 'fa': nx.Graph()}

for n in nx_graph.nodes():
    colors = nx_graph.nodes[n]["color"]

    for lang in ['en', 'zh', 'fa']:
        G = G_MAPS[lang]
        color_to_lang = eval(f"color_to_{lang}")
        name_to_lang = eval(f"name_to_{lang}")

        name = name_to_lang[nx_graph.nodes[n]["name_en"]]

        G.add_node('{name}')
        for c in colors:
            color = color_to_lang[c]
            G.add_node(f'{name}_{color}')
            G.add_edge(f'{name}', f'{name}_{color}', weight=0)
        for i in range(len(colors)):
            for j in range(i, len(colors)):
                G.add_edge(f'{name}_{color_to_lang[colors[i]]}', f'{name}_{color_to_lang[colors[j]]}', weight=1)

for s, t in nx_graph.edges():
    for lang in ['en', 'zh', 'fa']:
        G = G_MAPS[lang]
        color_to_lang = eval(f"color_to_{lang}")
        name_to_lang = eval(f"name_to_{lang}")
        s_name = name_to_lang[nx_graph.nodes[s]["name_en"]]
        s_colors = [color_to_lang[color] for color in nx_graph.nodes[s]["color"]]
        t_name = name_to_lang[nx_graph.nodes[t]["name_en"]]
        t_colors = [color_to_lang[color] for color in nx_graph.nodes[t]["color"]]
        for c in list(set(s_colors).intersection(set(t_colors))):
            G.add_edge(f'{s_name}_{c}', f'{t_name}_{c}', weight=1)


def MTR(source, target, lang="en"):
    source = MTR_map.get(source, source)
    target = MTR_map.get(target, target)
    G = G_MAPS[lang]
    shortest = nx.shortest_path(G, source=source, target=target)
    price = round((len(shortest) - 2) * 0.88 + 3.4, 2)
    time = (len(shortest) - 2) * 3
    if lang == "en":
        str_ret = ""
        str_ret += f"Take the {shortest[1].split('_')[1]} line of the {shortest[0]} station."
        for i in range(2, len(shortest) - 1):
            name, color = shortest[i].split("_")
            name_prev, color_prev = shortest[i - 1].split("_")
            if color != color_prev and name == name_prev:
                str_ret += f"Then change at {name} station from {color_prev} line to {color} line."
        str_ret += f"Get off the train at {shortest[-1]} station."
        return {"shortest_path": str_ret, "price": f"{price} HKD", "estimated_time": f"{time} mins"}
    elif lang == 'zh':
        str_ret = ""
        str_ret += f"请在{shortest[0]}站乘坐{shortest[1].split('_')[1]}线，"
        for i in range(2, len(shortest) - 1):
            name, color = shortest[i].split("_")
            name_prev, color_prev = shortest[i - 1].split("_")
            if color != color_prev and name == name_prev:
                str_ret += f"然后在{name}站换乘{color}线，"
        str_ret += f"最后在{shortest[-1]}站下车"
        return {"最短路线": str_ret, "价格": f"{price}港币", "预估时间": f"{time}分钟"}
    elif lang == 'fa':
        str_ret = ""
        str_ret += f"از خط {shortest[1].split('_')[1]} ایستگاه {shortest[0]} استفاده کنید."
        for i in range(2, len(shortest) - 1):
            name, color = shortest[i].split("_")
            name_prev, color_prev = shortest[i - 1].split("_")
            if color != color_prev and name == name_prev:
                str_ret += f"سپس در ایستگاه {name} از خط {color_prev} به خط {color} تغییر دهید."
        str_ret += f"در ایستگاه {shortest [-1]} از قطار پیاده شوید."
        return {"کوتاهترین_راه": str_ret, "قیمت": f"{price} HKD", "زمان_تخمین_زده_شده": f"{time}دقیقه "}
