import json
import dill as pickle
from datetime import datetime
from simoolator.cow import Cow
from .model_registry import ModelRegistry

class Herd:
    def __init__(self, name):
        self.name = name
        self.cows_in_herd = []
        self.model_registry = ModelRegistry()
        self.metadata = {}

    def __getstate__(self):
        state = {
            'name': self.name,
            'cows_in_herd': self.cows_in_herd,
            'model_registry': self.model_registry,
            'metadata': self.metadata
        }
        return state

    def __setstate__(self, state):
        self.name = state['name']
        self.cows_in_herd = state['cows_in_herd']
        self.model_registry = state['model_registry']
        self.metadata = state['metadata']

    def add_cow(self, cow):
        self.cows_in_herd.append(cow)

    def load_cows_from_json(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            for cow_data in data:
                cow = Cow(cow_id=cow_data['cow_id'], 
                          input_data=cow_data['input_data'])
                self.add_cow(cow)

    def execute_method(self, method_name, execution_mode='linear', *args, **kwargs):
        if execution_mode == 'linear':
            self._execute_linear(method_name, *args, **kwargs)
        elif execution_mode == 'cpu':
            self._execute_cpu(method_name, *args, **kwargs)
        elif execution_mode == 'gpu':
            self._execute_gpu(method_name, *args, **kwargs)
        else:
            raise ValueError("Invalid execution mode. Choose from 'linear', 'cpu', or 'gpu'.")

    def _execute_linear(self, method_name, *args, **kwargs):
        for cow in self.cows_in_herd:
            getattr(cow, method_name)(*args, **kwargs)

    def _execute_cpu(self, method_name, *args, **kwargs):
        raise NotImplementedError("Parallel CPU execution is not implemented yet.")

    def _execute_gpu(self, method_name, *args, **kwargs):
        raise NotImplementedError("GPU execution is not implemented yet.")
    
    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
        
    def register_model(self, model_function):
        if not self.cows_in_herd:
            raise ValueError("No cows in the herd to determine the input structure.")
        input_structure = self.cows_in_herd[0].input
        self.model_registry.register_model(model_function, input_structure)

    def execute_model(self, model_name, execution_mode='linear'):
        model_function, input_mapping = self.model_registry.get_model(model_name)
        
        if execution_mode == 'linear':
            self._execute_model_linear(model_function, input_mapping)
        elif execution_mode == 'cpu':
            self._execute_model_cpu(model_function, input_mapping)
        elif execution_mode == 'gpu':
            self._execute_model_gpu(model_function, input_mapping)
        else:
            raise ValueError("Invalid execution mode. Choose from 'linear', 'cpu', or 'gpu'.")

    def _execute_model_linear(self, model_function, input_mapping):
        start_time = datetime.now()
        exceptions = {}

        for cow in self.cows_in_herd:
            try:
                cow.run_model(model_function, input_mapping)
            except Exception as e:
                exceptions[cow.cow_id] = e
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
                
        metadata_entry = {
            'model_name': model_function.__name__,
            'execution_mode': 'linear',
            'start_time': start_time,
            'end_time': end_time,
            'execution_time_seconds': execution_time,
            'errors': exceptions
        }
        self.metadata[f'{model_function.__name__}_{start_time.date()}'] = metadata_entry
        
        if exceptions:
            print('\nThe following Cows failed to run the model: ')
            for cow_id, execption in exceptions.items():
                print(f'{cow_id}: {execption}')

    def _execute_model_cpu(self, model_function, input_mapping):
        raise NotImplementedError("Parallel CPU execution is not implemented yet.")

    def _execute_model_gpu(self, model_function, input_mapping):
        raise NotImplementedError("GPU execution is not implemented yet.")

    def list_cows(self):
        print('Index'.ljust(5), '| Cow ID')
        for index, cow in enumerate(self.cows_in_herd):
            print(f'{index}'.ljust(5), f'| {cow.cow_id}')

    def list_results(self, cow_index):
        cow = self.cows_in_herd[cow_index]
        cow._list_results()

    def get_result(self, cow_index, result_id):
        cow = self.cows_in_herd[cow_index]
        result = cow._get_result(result_id)
        return result

    def check_input(self):
        cow = self.cows_in_herd[0]
        cow._print_input_structure()
