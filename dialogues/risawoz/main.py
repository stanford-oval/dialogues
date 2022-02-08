import re
from ..main import Dataset


class Risawoz(Dataset):
	def __init__(self, name='risawoz'):
		super().__init__(name)
		
		self.state_re = re.compile('')
		self.knowledge_re = re.compile('')
		self.actions_re = re.compile('')
	
	def domain2api_name(self, domain):
		raise NotImplemented()
	
	def state2span(self, dialogue_state):
		raise NotImplemented()
	
	def span2state(self, state_span):
		raise NotImplemented()
	
	def process_data(self, args, root):
		raise NotImplemented()
	
	def make_api_call(self, dialogue_state, api_name, **kwargs):
		raise NotImplemented()
	
	def compute_metrics(self, args, prediction_path, reference_path):
		raise NotImplemented()
	
	def postprocess_prediction(self, prediction, **kwargs):
		pass
