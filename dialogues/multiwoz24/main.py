import copy
import re
from collections import defaultdict

import ujson

from ..main import Dataset


class Multiwoz24(Dataset):
    def __init__(self, name='multiwoz24'):
        super().__init__(name)

        self.state_re = re.compile('')
        self.knowledge_re = re.compile('')
        self.actions_re = re.compile('')

    def domain2api_name(self, domain):
        raise NotImplementedError

    def state2span(self, dialogue_state):
        raise NotImplementedError

    def span2state(self, state_span):
        raise NotImplementedError

    def process_state(self, state, **kwargs):
        belief = defaultdict(dict)
        for slot_value in state:
            assert slot_value['act'] == 'inform'

            assert len(slot_value['slots']) == 1
            domain_slot, value = slot_value['slots'][0]
            assert domain_slot.count('-') == 1
            domain, slot = domain_slot.split('-')

            assert isinstance(slot, str) and isinstance(value, str)

            # slot = slot.replace(' ', '-')

            # normalize so neural model can understand the words better
            # slot = slot.replace('pricerange', 'price-range')
            EXPERIMENT_DOMAINS = ["hotel", "train", "restaurant", "attraction", "taxi"]

            if value == 'none':
                value = None
            if domain not in EXPERIMENT_DOMAINS:
                value = None

            if value:
                # belief[domain][slot] = value
                belief[domain + '-' + slot] = value

        return belief

    def remove_extra_spaces(self, sent):
        for token in ['\t', '\n', ' ']:
            sent = sent.replace(token, ' ')
        sent = re.sub(r'\s{2,}', ' ', sent)
        return sent

    def process_agent_acts(self, acts_dict, ontology=None, **kwargs):
        acts = defaultdict(dict)
        for key, value in acts_dict.items():
            assert key.count('-') == 2
            domain, intent, slot = key.split('-', 2)

            # EXPERIMENT_DOMAINS = ["hotel", "train", "restaurant", "attraction", "taxi"]

            if slot in ['none', 'nooffer', 'ref']:
                continue
            if value in ['none']:
                value = None
            # if domain not in EXPERIMENT_DOMAINS:
            #     value = None

            if value:
                # belief[domain][slot] = value
                acts[key] = value

        return acts

    def state_dict2text(self, state, filtered=()):
        keys = list(state.keys())
        keys.sort()

        context = []
        for key in keys:
            value = state[key]
            if value in filtered:
                continue
            if value is None:
                continue
            if value == '':
                context.append(f'{key.replace("-", " ")} = " "')
            else:
                context.append(f'{key.replace("-", " ")} = " {value} "')

            context.append(',')

        if len(context) == 0:
            return 'null'

        return ' '.join(context).strip(', ')

    def process_data(self, args, root):
        splits = [split + '_dials_v2.json' for split in ['dev', 'train', 'test']]
        data_results = defaultdict(list)
        for split in splits:
            name = split.split('_')[0]
            data = ujson.load(open(root + split, 'r'))
            out_data = []
            for dlg in data:
                prev_belief_dict = dict()

                dlg_id = dlg['dialogue_idx']
                content = dlg['dialogue']
                turn_idx = 0

                while turn_idx < len(content):
                    turn = content[turn_idx]

                    EXPERIMENT_DOMAINS = ["hotel", "train", "restaurant", "attraction", "taxi"]
                    active_domain = turn['domain']

                    if active_domain not in EXPERIMENT_DOMAINS:
                        turn_idx += 1
                        continue

                    def get_lev_dict(belief_dict, prev_belief_dict):
                        lev_belief_dict = defaultdict(dict)
                        for domain_slot, value in belief_dict.items():
                            if domain_slot not in prev_belief_dict or prev_belief_dict[domain_slot] != value:
                                lev_belief_dict[domain_slot] = belief_dict[domain_slot]
                        return lev_belief_dict

                    belief_dict = self.process_state(turn['belief_state'])

                    user_utterance = self.remove_extra_spaces(turn["transcript"])
                    sys_utterance = self.remove_extra_spaces(turn["system_transcript"])

                    sys_acts = self.process_agent_acts(turn['system_acts'])

                    if not sys_utterance:
                        sys_utterance = '.'

                    # lev_dict = get_lev_dict(belief_dict, prev_belief_dict)
                    # lev_text = exp.state_dict2text(lev_dict)

                    belief_text = self.state_dict2text(belief_dict)
                    prev_belief_text = self.state_dict2text(prev_belief_dict)

                    acts = self.state_dict2text(sys_acts)

                    ex_id = f'{dlg_id}/{turn_idx}'

                    # context = ' '.join(['<state>', prev_belief_text, '<agent>', sys_utterance])
                    # question = ' '.join(['<user>', user_utterance])

                    input = ' '.join(
                        ["DST:", '<state>', prev_belief_text, '<endofstate>' '<acts>', acts, '<user>', user_utterance]
                    )

                    input = re.sub(r'\s{2,}', ' ', input)

                    out_string = '\t'.join([ex_id, input, belief_text])

                    # out_string = f'{ex_id}\t{prev_belief_text} ;{" " + sys_utterance if sys_utterance else ""}\t{user_utterance}\t{lev_text}'

                    out_data.append(out_string)

                    prev_belief_dict = copy.deepcopy(belief_dict)

                    turn_idx += 1

            data_results[name] = out_data

        return data_results['train'], data_results['dev'], data_results['test']

    def make_api_call(self, dialogue_state, api_name, **kwargs):
        raise NotImplementedError

    def compute_metrics(self, args, prediction_path, reference_path):
        raise NotImplementedError

    def postprocess_prediction(self, prediction, **kwargs):
        pass
