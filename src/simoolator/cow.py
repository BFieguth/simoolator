import random
import time
import numpy as np
from datetime import datetime

class Cow:
    def __init__(self, cow_id, input_data):
        self.cow_id = str(cow_id)
        self.input = input_data
        self.results = {}
        self.metadata = {}

    def __getstate__(self):
        state = {
            'cow_id': self.cow_id,
            'input': self.input,
            'results': self.results,
            'metadata': self.metadata
        }
        return state
    
    def __setstate__(self, state):
        self.cow_id = state['cow_id']
        self.input = state['input']
        self.results = state['results']
        self.metadata = state['metadata']

    def run_model(self, model_function, input_mapping):
        start_time = datetime.now()
        result_id = f'{model_function.__name__}_{start_time.date()}'
        inputs = {key: self._get_nested_value(value) for key, value in input_mapping.items()}
        result = model_function(**inputs)
        end_time = datetime.now()
        self.results[result_id] = result

        metadata_entry = {
            'model_name': model_function.__name__,
            'start_time': start_time,
            'end_time': end_time
        }
        self.metadata[result_id] = metadata_entry

    def _get_nested_value(self, path):
        keys = path.split('.')
        value = self.input
        for key in keys:
            value = value[key]
        return value
    
    def _list_results(self):
        print('Result ID'.ljust(25), '| Results')
        for result_id, data in self.results.items():
            print(f'{result_id}'.ljust(25), f'| {data}') 
    
    def _get_result(self, result_id):
        return self.results[result_id]

    def _print_input_structure(self):
        def print_structure(data, indent=0):    
            if isinstance(data, dict):
                for key, value in data.items():
                    print(' ' * indent + str(key))
                    if isinstance(value, dict):
                        print_structure(value, indent + 4)
                    else:
                        print(' ' * (indent + 4) + str(type(value).__name__))
            else:
                print(' ' * indent + str(type(data).__name__))
                
        print_structure(self.input)

    # Testing Methods #
    def moo(self):
        moo_sound = 'M' + 'o' * random.randint(2, 10)
        print(f"{self.cow_id}: {moo_sound}")

    def matrix_multiplication(self, n):
        """Perform an intensive computation with matrix multiplications."""
        start_time = time.time()
        # Create large random matrices
        A = np.random.rand(n, n)
        B = np.random.rand(n, n)
        for _ in range(100):
            C = np.dot(A, B)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Cow {self.cow_id} performed intensive computation in {elapsed_time:.2f} seconds.")
        self.results['time'] = elapsed_time
        