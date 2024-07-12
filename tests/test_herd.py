import datetime
import json
import unittest.mock

import pytest

from simoolator.cow import Cow
from simoolator.herd import Herd
from simoolator.model_registry import ModelRegistry
import simoolator.utils as utils


class TestHerd:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.herd = Herd(name="TestHerd")
        self.cow1 = Cow(cow_id=1, input_data={"milk": {"morning": 10, "evening": 8},
                                              "weight": 500})
        self.cow2 = Cow(cow_id=2, input_data={"milk": {"morning": 12, "evening": 9},
                                              "weight": 740})
        self.herd.add_cow(self.cow1)
        self.herd.add_cow(self.cow2)

    def test_initialization(self):
        assert self.herd.name == "TestHerd"
        assert len(self.herd.cows_in_herd) == 2
        assert isinstance(self.herd.model_registry, ModelRegistry)
        assert self.herd.metadata == {}

    def test_getstate(self):
        state = self.herd.__getstate__()
        expected_state = {
            "name": self.herd.name,
            "cows_in_herd": self.herd.cows_in_herd,
            "model_registry": self.herd.model_registry,
            "metadata": self.herd.metadata
        }
        assert state == expected_state

    def test_setstate(self):
        state = {
            "name": "NewHerd",
            "cows_in_herd": [self.cow1],
            "model_registry": unittest.mock.MagicMock(),
            "metadata": {"meta": "data"}
        }
        self.herd.__setstate__(state)
        assert self.herd.name == "NewHerd"
        assert self.herd.cows_in_herd == [self.cow1]
        assert self.herd.model_registry == state["model_registry"]
        assert self.herd.metadata == {"meta": "data"}

    def test_add_cow(self):
        cow3 = Cow(cow_id=3, input_data={"milk": {"morning": 14, "evening": 10}})
        self.herd.add_cow(cow3)
        assert len(self.herd.cows_in_herd) == 3
        assert self.herd.cows_in_herd[-1] == cow3

    def test_load_cows_from_json(self, tmpdir):
        cows_data = [
            {"cow_id": 3, "input_data": {"milk": {"morning": 14, "evening": 10}}},
            {"cow_id": 4, "input_data": {"milk": {"morning": 16, "evening": 11}}}
        ]
        file = tmpdir.join("cows.json")
        file.write(json.dumps(cows_data))
        self.herd.load_cows_from_json(str(file))
        assert len(self.herd.cows_in_herd) == 4
        assert self.herd.cows_in_herd[-1].cow_id == "4"

    def test_save_and_load(self, tmpdir):
        file = tmpdir.join("herd.pkl")
        self.herd.save(str(file))
        loaded_herd = Herd.load(str(file))
        assert loaded_herd.name == self.herd.name
        assert len(loaded_herd.cows_in_herd) == 2

    def test_execute_method(self):
        with unittest.mock.patch.object(Cow, 'run_model') as mock_run_model:
            self.herd.execute_method('run_model', lambda x: x)
            assert mock_run_model.call_count == 2

    def test_register_model(self):
        model_function = lambda milk: milk
        expected_mapping = {'milk': 'milk'}

        self.herd.register_model(model_function)
        registered_model = self.herd.model_registry.models[model_function.__name__]
        assert registered_model['function'] == model_function
        assert registered_model['input_mapping'] == expected_mapping

    def test_execute_model(self):
        model_function = lambda milk: milk
        self.herd.register_model(model_function)
        
        with unittest.mock.patch.object(Herd, '_execute_model_linear') as mock_execute_model_linear:
            self.herd.execute_model(model_function.__name__, 'linear')
            mock_execute_model_linear.assert_called_once()

    def test_list_cows(self, capsys):
        self.herd.list_cows()
        captured = capsys.readouterr()
        output_lines = captured.out.split('\n')
        assert "0     | 1" in output_lines
        assert "1     | 2" in output_lines

    def test_list_results(self, capsys):
        with unittest.mock.patch.object(Cow, 'list_results') as mock_list_results:
            self.herd.list_results(0)
            mock_list_results.assert_called_once()

    def test_get_result(self):
        with unittest.mock.patch.object(Cow, 'get_result') as mock_get_result:
            mock_get_result.return_value = 100
            result = self.herd.get_result(0, 'result1')
            assert result == 100

    def test_check_input(self, capsys):
        self.herd.check_input()
        captured = capsys.readouterr()
        assert 'milk' in captured.out

    def test_check_data_consistency(self):
        assert self.herd.check_data_consistency() == True
        cow3 = Cow(cow_id=3, input_data={"milk": {"morning": 10}})
        self.herd.add_cow(cow3)
        assert self.herd.check_data_consistency() == False

    def test_get_input_mapping(self):
        with unittest.mock.patch.object(utils, 'print_nested_dict_tree') as mock_print_nested_dict_tree:
            self.herd.model_registry.get_model = unittest.mock.MagicMock(return_value=(None, {"milk": {"morning": "int"}}))
            self.herd.get_input_mapping('dummy_model')
            mock_print_nested_dict_tree.assert_called_once()

    def test_list_models_verbose(self, capsys):
        def model_function(milk, weight):
            return milk + weight

        self.herd.register_model(model_function)

        self.herd.list_models(verbose=True)
        captured = capsys.readouterr()

        assert "-------------------------" in captured.out
        assert model_function.__name__ in captured.out
        assert "milk" in captured.out
        assert "weight" in captured.out

    def test_list_models_non_verbose(self, capsys):
        def model_function(milk, weight):
            return milk + weight
        
        self.herd.register_model(model_function)

        self.herd.list_models(verbose=False)
        captured = capsys.readouterr()

        assert "Model" in captured.out
        assert model_function.__name__ in captured.out
        assert "milk" in captured.out
        assert "weight" in captured.out

    def test_remove_model(self, capsys):
        model_function = lambda milk: milk
        self.herd.register_model(model_function)
        assert model_function.__name__ in self.herd.model_registry.models

        self.herd.remove_model(model_function.__name__)
        captured = capsys.readouterr()

        assert model_function.__name__ not in self.herd.model_registry.models
        assert f"{model_function.__name__} has been removed." in captured.out

    def test_remove_model_not_registered(self, capsys):
        self.herd.remove_model("non_existent_model")
        captured = capsys.readouterr()

        assert "ERROR: non_existent_model is not registered." in captured.out

    def test_get_model(self):
        model_function = lambda milk: milk
        self.herd.register_model(model_function)

        retrieved_function = self.herd.get_model(model_function.__name__)
        assert retrieved_function == model_function

    def test_get_model_not_registered(self, capsys):
        retrieved_function = self.herd.get_model("non_existent_model")
        captured = capsys.readouterr()

        assert retrieved_function is None
        assert "non_existent_model is not registered" in captured.out
