import argparse
import json

import requests

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default='en')
    parser.add_argument('--model_url', default="http://localhost:8080/v1/models/nlp:predict")
    parser.add_argument('--acts_file', required=True, help='path to file with input_acts')
    parser.add_argument('--processed_data_file', help='path to json file that has gold natural language responses')
    parser.add_argument('--output_file', required=True, help='path to output file with natural responses')
    parser.add_argument('--batch_size', default=20)

    args = parser.parse_args()

    if args.processed_data_file:
        gold_responses = []
        with open(args.processed_data_file) as fin:
            data = json.load(fin)['data']
            for item in data:
                if 'response' in item:
                    gold_responses.append(item['response'])

    idx = 0
    batch = []
    batch_golds = []
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
                    batch_golds.append(gold_responses[idx])
                    idx += 1
                batch.append({"context": sent, "question": ""})

                if len(batch) == args.batch_size:
                    request = json.dumps({"id": "null", "task": "bitod", "instances": batch})
                    response = requests.post(args.model_url, data=request)
                    preds = json.loads(response.text)["predictions"]
                    new_sents = [pred["answer"] for pred in preds]
                    for new_sent, gold in zip(new_sents, batch_golds):
                        fout.write('\t'.join([id_, new_sent, gold]) + '\n')
                    batch = []
                    batch_golds = []

        if len(batch):
            request = json.dumps({"id": "null", "task": "bitod", "instances": batch})
            response = requests.post(args.model_url, data=request)
            preds = json.loads(response.text)["predictions"]
            new_sents = [pred["answer"] for pred in preds]
            for new_sent, gold in zip(new_sents, batch_golds):
                fout.write('\t'.join([id_, new_sent, gold]) + '\n')
