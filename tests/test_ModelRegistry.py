from typing import Callable, Dict, Any

import pytest

from simoolator.model_registry import ModelRegistry

class TestModelRegistry:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.registry = ModelRegistry()

    def test_initialization(self):
        assert self.registry.models == {}
    
    def test_register_model(self):
        model_function = lambda milk: milk
        input_structure = {'milk': {'morning': 10, 'evening': 8}}

        self.registry.register_model(model_function, input_structure)

        assert model_function.__name__ in self.registry.models
        registered_model = self.registry.models[model_function.__name__]
        assert registered_model['function'] == model_function
        assert registered_model['input_mapping'] == {'milk': 'milk'}

    def test_get_model(self):
        model_function = lambda milk: milk
        input_structure = {'milk': {'morning': 10, 'evening': 8}}
        self.registry.register_model(model_function, input_structure)

        retrieved_function, input_mapping = self.registry.get_model(model_function.__name__)

        assert retrieved_function == model_function
        assert input_mapping == {'milk': 'milk'}

    def test_get_model_not_registered(self):
        with pytest.raises(ValueError, match="Model non_existent_model is not registered."):
            self.registry.get_model('non_existent_model')
    
    def test_determine_input_mapping(self):
        def model_function(milk, weight):
            return milk + weight
        
        input_structure = {
            'milk': {'morning': 10, 'evening': 8},
            'weight': 500,
            'health': {'temperature': 101.5, 'heart_rate': 60}
        }
        
        expected_mapping = {
            'milk': 'milk',
            'weight': 'weight'
        }
        
        input_mapping = self.registry._determine_input_mapping(model_function, input_structure)
        assert input_mapping == expected_mapping
