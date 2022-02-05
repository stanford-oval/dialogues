from ..main import Dataset


class Risawoz(Dataset):
	def __init__(self, name):
		super().__init__(name)
	
	def process_data(self, args, root):
		raise NotImplemented()
	
	def make_api_call(self, dialogue_state, api_name, **kwargs):
		raise NotImplemented()
	
	def compute_metrics(self, args, prediction_path, reference_path):
		raise NotImplemented()
