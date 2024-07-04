import inspect
from typing import Callable, Tuple

class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register_model(self, 
                       model_function: Callable, 
                       input_structure: dict
) -> None:
        """
        Add new model function to registry with input mapping

        Args:
            model_function::Callalbe
                Function to add to registry

            input_structure::dict
                Mapping of function arguments to data structure of Cow
        """
        input_mapping = self._determine_input_mapping(
            model_function, input_structure
            )
        self.models[model_function.__name__] = {
            'function': model_function,
            'input_mapping': input_mapping
        }

    def _determine_input_mapping(self, 
                                 model_function: Callable, 
                                 input_structure: dict
) -> dict:
        """
        Match arguments names with path to value in a nested dictionary

        Args:
            model_function::Callable
                Function to map arguments for

            input_structure::dict
                Structure of the input data to map
        """
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
    
    def get_model(self, model_name: str) -> Tuple[str, dict]:
        """
        Return a model function and the input mapping
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not registered.")
        return self.models[model_name]['function'], self.models[model_name]['input_mapping']
