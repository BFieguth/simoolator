import inspect

class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register_model(self, model_function, input_structure):
        input_mapping = self._determine_input_mapping(model_function, input_structure)
        self.models[model_function.__name__] = {
            'function': model_function,
            'input_mapping': input_mapping
        }

    def _determine_input_mapping(self, model_function, input_structure):
        def find_paths(input_structure, keys):
            paths = {}

            def recursive_search(current_structure, current_path):
                if isinstance(current_structure, dict):
                    for key, value in current_structure.items():
                        new_path = current_path + [key]
                        if key in keys:
                            paths[key] = '.'.join(new_path)
                            keys.remove(key)
                        if isinstance(value, dict) and keys:
                            recursive_search(value, new_path)

            recursive_search(input_structure, [])
            return paths

        signature = inspect.signature(model_function)
        keys = list(signature.parameters.keys())
        input_mapping = find_paths(input_structure, keys)
        return input_mapping
    
    def get_model(self, model_name):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not registered.")
        return self.models[model_name]['function'], self.models[model_name]['input_mapping']
