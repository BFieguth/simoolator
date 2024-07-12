import datetime
import inspect
from typing import Any, Callable, Dict, Union

class Cow:
    """
    The Cow class stores data for an individual animal. When methods are run at
    the Herd level, the results are store within each individual Cow instance.
    """
    # Initalization and state management
    def __init__(self, cow_id: Union[int, float, str], input_data: Any) -> None:
        """
        Initialize a new Cow instance.

        Args:
            cow_id: Unique identifier for the cow.
            input_data: Data associated with the cow.
        """
        self.cow_id = str(cow_id)
        self.input = input_data
        self.results = {}
        self.metadata = {}

    def __getstate__(self) -> Dict[str, Any]:
        """
        Data to include when serializing.
        """
        state = {
            "cow_id": self.cow_id,
            "input": self.input,
            "results": self.results,
            "metadata": self.metadata
        }
        return state
    
    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Data to extract when loading from pickle.
        """
        self.cow_id = state["cow_id"]
        self.input = state["input"]
        self.results = state["results"]
        self.metadata = state["metadata"]

    # Core Functionality
    def run_model(self, 
                  model_function: Callable, 
                  input_mapping: Dict[str, str]
    ) -> None:
        """
        Run a model function using input_mapping to map self to function arguments

        Args:
            model_function::Callable
                Function to run
            input_mapping::dict
                Mapping of self to model_function arguments
        """
        
        def get_nested_value(path: str) -> Any:
            """
            Return value nested in self.input.

            Args:
                path: Dot-separated path to the nested value.
            """
            keys = path.split(".")
            value = self.input
            for key in keys:
                value = value[key]
            return value
        
        start_time = datetime.datetime.now()
        formatted_start_time = start_time.isoformat()
        result_id = f"{model_function.__name__}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        inputs = {key: get_nested_value(value) for key, value in input_mapping.items()}

        # Extract default args used for metadata
        sig = inspect.signature(model_function)
        defaults = {key: val.default for key, val in sig.parameters.items() 
                    if val.default is not inspect.Parameter.empty}
        used_defaults = {key: val for key, val in defaults.items() 
                         if key not in input_mapping}

        result = model_function(**inputs)
        end_time = datetime.datetime.now()
        formatted_end_time = end_time.isoformat()
        self.results[result_id] = result

        metadata_entry = {
            "model_name": model_function.__name__,
            "start_time": formatted_start_time,
            "end_time": formatted_end_time,
            "run_time": end_time - start_time,
            "input_args": inputs,
            "default_args": used_defaults,
            # "status": , # TODO once error handling is setup add a status variable
                          # Did model run or crash
            # "error_message": , # If model crashed store the error message 
        }
        self.metadata[result_id] = metadata_entry
    
    def list_results(self) -> None:
        """
        Display all the model results.
        """
        print("Result ID".ljust(25), "| Results")
        for result_id, data in self.results.items():
            print(f"{result_id}".ljust(25), f"| {data}") 
    
    def get_result(self, result_id: str) -> Any:
        """
        Return a specific result. 

        Args:
            result_id: ID value for results to return.
        """
        return self.results[result_id]

    # Data structure visualization
    def print_input_structure(self) -> None:
        """
        Print the variable names and type of self.input. 
        """
        def print_structure(data, indent=0):    
            if isinstance(data, dict):
                for key, value in data.items():
                    print(" " * indent + str(key))
                    if isinstance(value, dict):
                        print_structure(value, indent + 4)
                    else:
                        print(" " * (indent + 4) + str(type(value).__name__))
            else:
                print(" " * indent + str(type(data).__name__))
                
        print_structure(self.input)

    def get_input_structure(self) -> Dict[str, Any]:
        """
        Returns the structure of self.input with key names and data types.
        Used to check all Cow instances have the same input structure.
        """
        def _get_structure(data: Any) -> Any:
            if isinstance(data, dict):
                return {key: _get_structure(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [_get_structure(item) for item in data]
            else:
                return type(data).__name__ 
        return _get_structure(self.input)
            