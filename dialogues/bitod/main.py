import logging
import os.path
from collections import defaultdict

from ..main import Dataset
from .BiToD.knowledgebase import api
from .BiToD.knowledgebase.en_zh_mappings import r_en_API_MAP
from .BiToD.preprocess import prepare_data
from .BiToD.evaluate import eval_file
from .BiToD.utils import state2constraints


logger = logging.getLogger(__name__)

class Bitod(Dataset):
	def __init__(self, name='bitod'):
		super().__init__(name)
	
	def process_data(self, args, root):
		if args.setting in ["en", "zh2en"]:
			path_train = ["data/en_train.json"]
			path_dev = ["data/en_valid.json"]
			path_test = ["data/en_test.json"]
		elif args.setting in ["zh", "en2zh"]:
			path_train = ["data/zh_train.json"]
			path_dev = ["data/zh_valid.json"]
			path_test = ["data/zh_test.json"]
		else:
			path_train = ["data/zh_train.json", "data/en_train.json"]
			path_dev = ["data/zh_valid.json", "data/en_valid.json"]
			path_test = ["data/zh_test.json", "data/en_test.json"]
			
		path_train = [os.path.join(root, p) for p in path_train]
		path_dev = [os.path.join(root, p) for p in path_dev]
		path_test = [os.path.join(root, p) for p in path_test]
		
		train, dev, test = prepare_data(args, path_train, path_dev, path_test)
		return train, dev, test
	
	def make_api_call(self, dialogue_state, api_name, src_lang='en', dial_id=None, turn_id=None):
		constraints = state2constraints(dialogue_state[api_name])
		knowledge = defaultdict(dict)
		result = [0, 0, 0]
		
		try:
			result = api.call_api(r_en_API_MAP.get(api_name, api_name), constraints=[constraints], lang=src_lang)
		except Exception as e:
			logger.error(f'Error: {e}')
			logger.error(
				f'Failed API call with api_name: {api_name}, constraints: {constraints}, processed_query: {result[2]}, for turn: {dial_id}/{turn_id}'
			)
		
		if int(result[1]) <= 0:
			logger.warning(
				f'Message = No item available for api_name: {api_name}, constraints: {constraints},'
				f' processed_query: {result[2]}, for turn: {dial_id}/{turn_id}'
			)
			
		else:
			# always choose the highest ranking results (so we have deterministic api results)
			knowledge[api_name].update(result[0])
		
		return knowledge
	
	def compute_metrics(self, args, prediction_path, reference_path):
		results = eval_file(args, prediction_path, reference_path)
		return results
