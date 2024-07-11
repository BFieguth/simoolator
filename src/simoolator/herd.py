from datetime import datetime
import json
from typing import Any, Callable, Dict

import dill as pickle

from simoolator.cow import Cow
from simoolator.model_registry import ModelRegistry
import simoolator.utils as utils

class Herd:
    """
    The Herd class manages a collection of Cow instances and executes models on them.
    """
    # Initialization and State Management
    def __init__(self, name: str) -> None:
        """
        Initialize a new Herd instance.

        Args:
            name: Name of the herd.
        """
        self.name = name
        self.cows_in_herd = []
        self.model_registry = ModelRegistry()
        self.metadata = {}

    def __getstate__(self) -> Dict[str, Any]:
        """
        Data to include when serializing.
        """
        state = {
            "name": self.name,
            "cows_in_herd": self.cows_in_herd,
            "model_registry": self.model_registry,
            "metadata": self.metadata
        }
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Data to extract when loading from pickle.
        """
        self.name = state["name"]
        self.cows_in_herd = state["cows_in_herd"]
        self.model_registry = state["model_registry"]
        self.metadata = state["metadata"]

    def add_cow(self, cow: Cow) -> None:
        """
        Add a cow to the herd.

        Args:
            cow: Cow instance to add.
        """
        self.cows_in_herd.append(cow)

    def load_cows_from_json(self, filename: str) -> None:
        with open(filename, "r") as file:
            data = json.load(file)
            for cow_data in data:
                cow = Cow(cow_id=cow_data["cow_id"], 
                          input_data=cow_data["input_data"])
                self.add_cow(cow)
    
    def save(self, filename: str) -> None:
        """
        Save the Herd instance to a pickle file.

        Args:
            filename: Path to the file.
        """
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filename: str) -> "Herd":
        """
        Load a Herd instance from a pickle file.

        Args:
            filename: Path to the file.

        Returns:
            Loaded Herd instance.
        """
        with open(filename, "rb") as file:
            return pickle.load(file)
     
    # Execution Methods
    def execute_method(self, method_name: str, *args, **kwargs) -> None:
        """
        Execute a method on all cows in the herd.

        Args:
            method_name: Name of the method to execute.
        """
        for cow in self.cows_in_herd:
            getattr(cow, method_name)(*args, **kwargs)

    def execute_model(self, 
                      model_name: str, 
                      execution_mode: str = "linear"
    ) -> None:
        """
        Execute a registered model on all cows in the herd.

        Args:
            model_name: Name of the model to execute.
            execution_mode: Execution mode ('linear', 'cpu', 'gpu').
        """
        model_function, input_mapping = self.model_registry.get_model(model_name)
        if execution_mode == "linear":
            self._execute_model_linear(model_function, input_mapping)
        elif execution_mode == "cpu":
            self._execute_model_cpu(model_function, input_mapping)
        elif execution_mode == "gpu":
            self._execute_model_gpu(model_function, input_mapping)
        else:
            raise ValueError("Invalid execution mode. Choose from 'linear', 'cpu', or 'gpu'.")

    def _execute_model_linear(self, 
                              model_function: Callable, 
                              input_mapping: Dict[str, str]
    ) -> None:
        """
        Execute a model on all cows in the herd sequentially.

        Args:
            model_function: Model function to execute.
            input_mapping: Mapping of inputs for the model function.
        """
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
            "model_name": model_function.__name__,
            "execution_mode": "linear",
            "start_time": start_time,
            "end_time": end_time,
            "execution_time_seconds": execution_time,
            "errors": exceptions
        }
        self.metadata[f"{model_function.__name__}_{start_time.strftime('%Y%m%d_%H%M%S')}"] = metadata_entry
        
        if exceptions:
            print("\nThe following Cows failed to run the model: ")
            for cow_id, execption in exceptions.items():
                print(f'{cow_id}: {execption}')

    def _execute_model_cpu(self, 
                           model_function: Callable, 
                           input_mapping: Dict[str, str]
    ) -> None:
        """
        Execute a model on all cows in the herd using parallel CPU execution.
        """
        raise NotImplementedError("Parallel CPU execution is not implemented yet.")

    def _execute_model_gpu(self, 
                           model_function: Callable, 
                           input_mapping: Dict[str, str]
    ) -> None:
        """
        Execute a model on all cows in the herd using GPU execution.
        """
        raise NotImplementedError("GPU execution is not implemented yet.")

    # Model Registration
    def register_model(self, model_function: Callable) -> None:
        """
        Register a model function in the ModelRegistry.

        Args:
            model_function: Function to register.
        """
        if not self.cows_in_herd:
            raise ValueError("No cows in the herd to determine the input structure.")
        input_structure = self.cows_in_herd[0].input
        self.model_registry.register_model(model_function, input_structure)

    # Utilities and Information
    def list_cows(self) -> None:
        """Display all cows in the herd."""
        print("Index".ljust(5), "| Cow ID")
        for index, cow in enumerate(self.cows_in_herd):
            print(f"{index}".ljust(5), f"| {cow.cow_id}")

    def list_results(self, cow_index: int) -> None:
        """
        Display results for a specific cow.

        Args:
            cow_index: Index of the cow in the herd.
        """
        cow = self.cows_in_herd[cow_index]
        cow.list_results()

    def get_result(self, cow_index: int, result_id: str) -> Any:
        """
        Return a specific result for a specific cow.

        Args:
            cow_index: Index of the cow in the herd.
            result_id: ID of the result to return.
        """
        cow = self.cows_in_herd[cow_index]
        result = cow.get_result(result_id)
        return result

    def check_input(self) -> None:
        """
        Display the input structure of the first cow in the herd.
        """
        cow = self.cows_in_herd[0]
        cow.print_input_structure()

    def check_data_consistency(self) -> bool:
        """
        Check that all cows in the herd have a consistent input structure.

        Returns:
            True if all cows have a consistent input structure, False otherwise.
        """
        if not self.cows_in_herd:
            return True
        
        inconsistent_cows = []
        first_instance = self.cows_in_herd[0].get_input_structure()
        for cow in self.cows_in_herd[1:]:
            if cow.get_input_structure() != first_instance:
                inconsistent_cows.append(cow.cow_id)
    
        if inconsistent_cows:
            print(f"The following cow IDs have issues with their input data: {inconsistent_cows}")
            return False
        return True

    def get_input_mapping(self, model_name: str) -> None:
        """
        Display the input mapping for a registered model.

        Args:
            model_name: Name of the model.
        """
        if self.check_data_consistency():
            _ , input_mapping = self.model_registry.get_model(model_name)
            input_data = self.cows_in_herd[0].input
            utils.print_nested_dict_tree(
                input_data, input_mapping=(model_name, input_mapping)
                )
        else:
            raise ValueError("Structure of input data is inconsistent across herd")
        