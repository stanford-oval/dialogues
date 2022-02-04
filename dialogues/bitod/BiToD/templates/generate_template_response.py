import argparse
import json
import os

from BiToD.knowledgebase.en_zh_mappings import api_names, zh2en_ACT_MAP, zh2en_API_MAP, zh2en_RELATION_MAP, zh2en_SLOT_MAP
from BiToD.utils import span2action


class TemplateResponseGenerator(object):
    def __init__(self, lang, filename='human', template_dir=None):
        self.lang = lang
        if not template_dir:
            template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
        self.template_dir = template_dir
        templates = {}
        with open(os.path.join(self.template_dir, lang, f'{filename}.tsv')) as fin:
            for line in fin:
                id_, template = line.strip('\n').split('\t')
                # sanity check
                assert id_.count('@') == template.count('@'), (id_, template)
                templates[id_] = template
        self.templates = templates
        self.api_names = api_names

    def generate(self, acts):
        try:
            acts_dict = span2action(acts, self.api_names)
        except:
            print(f'Prediction contains slots not part of ontology (i.e. model hallucinated): {acts}')
            return 'None'
        # domains = list(processed_acts.keys())
        # keys.sort()

        context = []
        for domain_intent, asrvs in acts_dict.items():
            if self.lang == 'zh':
                domain_intent = zh2en_API_MAP[domain_intent]
                domain, intent = domain_intent.split('_')[0], domain_intent.split('_')[-1]
            else:
                domain, intent = domain_intent.split(' ')
            for item in asrvs:
                act, slot, relation, value = item['act'], item['slot'], item['relation'], item['value']
                if self.lang == 'zh':
                    act = zh2en_ACT_MAP[act]
                    slot = zh2en_SLOT_MAP[slot]
                    relation = zh2en_RELATION_MAP[relation]

                new_key = f'{domain}!!{act}!!{slot}'
                if len(value) != 1:
                    if relation == 'one_of':
                        print('No support for multiple values yet')
                        continue
                    else:
                        value = [' | '.join(value)]
                assert len(value) == 1
                value = str(value[0])

                if value != 'null':
                    new_key += '!!@'

                if self.lang == 'zh':
                    if new_key not in self.templates:
                        if slot == 'start_date':
                            new_key = new_key.replace('start_date', 'date')
                        # original dataset bug
                        if new_key == 'restaurants!!offer!!cuisine':
                            new_key = 'restaurants!!offer!!cuisine!!@'
                if new_key not in self.templates:
                    print('Failed to templatize')
                    print(new_key, acts)
                    continue
                template_text = self.templates[new_key].replace('@', value)

                context.append(template_text)

        return ' '.join(context)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default='en')
    parser.add_argument('--template_name', default='human')
    parser.add_argument('--acts_file', required=True, help='path to file with input_acts')
    parser.add_argument('--processed_data_file', help='path to json file that has gold natural language responses')
    parser.add_argument('--output_file', required=True, help='path to output file with natural responses')
    args = parser.parse_args()

    templates = TemplateResponseGenerator(args.language, filename=args.template_name)

    # en_acts = '( attractions search )'
    #         ' offer address equal_to " 28 شان مونگ سړک ، کولوون " ,'
    #         ' offer name equal_to " اتاق چای گربه ها " ,'
    #         ' offer phone_number equal_to " +62 818-0919-0764 " ,'
    #         ' offer rating equal_to " 7 "'

    # zh_acts = '( 餐馆预订 ) ' \
    #        '确认 人数 等于 " 十一 " , ' \
    #        '确认 名字 等于 " 铃木屋 " , ' \
    #        '确认 时间 等于 " 下午7:40 " , ' \
    #        '确认 预订日期 等于 " 七月十二号 "'

    if args.processed_data_file:
        gold_responses = []
        with open(args.processed_data_file) as fin:
            data = json.load(fin)['data']
            for item in data:
                if 'response' in item:
                    gold_responses.append(item['response'])

    idx = 0
    with open(args.acts_file) as fin, open(args.output_file, 'w') as fout:
        for line in fin:
            parts = line.strip('\n').split('\t')
            if len(parts) == 1:
                sent = parts[0]
            elif len(parts) == 2:
                id_, sent = parts
            elif len(parts) == 3:
                id_, sent, gold = parts
            else:
                raise ValueError(f'Malformed input: {line}')

            if 'response' in id_:
                if args.processed_data_file:
                    gold = gold_responses[idx]
                    idx += 1
                new_sent = templates.generate(sent)
            else:
                new_sent = sent

            fout.write('\t'.join([id_, new_sent, gold]) + '\n')
