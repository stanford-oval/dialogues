import re


class Dataset(object):
    def __init__(self, name):

        # name of the dataset
        self.name = name

        # regex to extract belief state span from input
        self.state_re = re.compile('')

        # regex to extract knowledge span (api results) from input
        self.knowledge_re = re.compile('')

        # regex to extract agent dialogue acts from input
        self.actions_re = re.compile('')

    def domain2api_name(self, domain):
        """
        map domain name to api name used to query the database. these can be the same.
        :param domain: str
        :return: str
        """
        raise NotImplementedError

    def state2span(self, dialogue_state):
        """
        converts dictionary of dialogue state to a text span
        :param dialogue_state: dict
        :return: str
        """
        raise NotImplementedError

    def span2state(self, state_span):
        """
        converts dialogue state text span to a dictionary
        :param state_span: str
        :return: dict
        """
        raise NotImplementedError

    def update_state(self, lev, cur_state):
        """
        Updates cur_state according to the levenshtein state
        :param lev: dict
        :param cur_state: dict
        :return: dict
        """
        raise NotImplementedError

    def process_data(self, args, root):
        """
        converts raw dataset to the format accepted by genienlp
        each dialogue turn is broken down into 4 subtasks:
        Dialogue State Tracking (DST), API call decision (API) , Dialogue Act generation (DA), Response Generation (RG)
        :param args: dictionary of arguments passed to underlying data processor
        :param root: path to folder containing data files
        :return: three lists containing dialogues for each data split
        """
        raise NotImplementedError

    def make_api_call(self, dialogue_state, api_name, **kwargs):
        """
        given dialogue state and api_name, compute the constraints for api call, make the call, and return the results in text form
        :param dialogue_state: dict
        :param api_name: str
        :param kwargs: additional args to pass to api call function
        :return: a dictionary of constraints used as input to api caller
        :return: results of api call in text form
        """
        raise NotImplementedError

    def compute_metrics(self, args, prediction_path, reference_path):
        """
        compare predictions vs gold and compute metrics. prediction file should contain model predictions for each subtask for each turn.
        reference file can be the original raw data file or a preprocessed version if it contains all needed info to calculate the required metrics
        :param args: dictionary of arguments passed to underlying evaluation code
        :param prediction_path: path to file containing model predictions
        :param reference_path: path to file containing gold values to compare predictions against
        :return: a dictionary with metric names as keys and their computed values (in percentage)
        """
        raise NotImplementedError

    def postprocess_prediction(self, prediction, **kwargs):
        """
        rule-based postprocessings done on model predictions
        :param prediction: str
        :param kwargs: additional args used for postprocessing
        :return: modified prediction
        """
        pass
