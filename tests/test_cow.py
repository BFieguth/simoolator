import datetime

import pytest

from simoolator.cow import Cow


class TestCow:
    @pytest.fixture(autouse=True)
    def setup(self):
        input_data = {
            "milk": {"morning": 10, "evening": 8},
            "weight": 500,
            "health": {"temperature": 101.5, "heart_rate": 60}
        }
        self.cow = Cow(cow_id=1, input_data=input_data)

    def test_initialization(self):
        assert self.cow.cow_id == "1"
        assert self.cow.input == {
            "milk": {"morning": 10, "evening": 8},
            "weight": 500,
            "health": {"temperature": 101.5, "heart_rate": 60}
        }
        assert self.cow.results == {}
        assert self.cow.metadata == {}

    def test_getstate(self): 
        state = self.cow.__getstate__()
        expected_state = {
            "cow_id": "1",
            "input": self.cow.input,
            "results": self.cow.results,
            "metadata": self.cow.metadata
        }
        assert state == expected_state

    def test_setstate(self):
        state = {
            "cow_id": "2",
            "input": {"milk": 12},
            "results": {"result1": 100},
            "metadata": {"meta1": "data"}
        }
        self.cow.__setstate__(state)
        assert self.cow.cow_id == "2"
        assert self.cow.input == {"milk": 12}
        assert self.cow.results == {"result1": 100}
        assert self.cow.metadata == {"meta1": "data"}

    def test_run_model(self):
        def dummy_model(milk, weight):
            return milk["morning"] + milk["evening"] + weight

        input_mapping = {
            "milk": "milk",
            "weight": "weight"
        }
        self.cow.run_model(dummy_model, input_mapping)

        result_id = list(self.cow.results.keys())[0]
        result = self.cow.results[result_id]
        assert result == 518

        metadata = self.cow.metadata[result_id]
        assert metadata["model_name"] == "dummy_model"
        assert "start_time" in metadata
        assert "end_time" in metadata
        assert "run_time" in metadata
        assert metadata["input_args"] == {
            "milk": self.cow.input["milk"], 
            "weight": self.cow.input["weight"]
            }
        assert metadata["default_args"] == {}
        
    def test_get_nested_value(self):
        value = self.cow._get_nested_value("milk.morning")
        assert value == 10

    def test_list_results(self, capsys):
        self.cow.results = {"result1": 100, "result2": 200}
        self.cow.list_results()
        captured = capsys.readouterr()
        assert "result1" in captured.out
        assert "result2" in captured.out
        assert "| 100" in captured.out
        assert "| 200" in captured.out

    def test_get_result(self):
        self.cow.results = {"result1": 100}
        result = self.cow.get_result("result1")
        assert result == 100

    def test_print_input_structure(self, capsys):
        self.cow.print_input_structure()
        captured = capsys.readouterr()
        assert "milk" in captured.out
        assert "weight" in captured.out
        assert "health" in captured.out

    def test_get_input_structure(self):
        structure = self.cow.get_input_structure()
        expected_structure = {
            "milk": {"morning": "int", "evening": "int"},
            "weight": "int",
            "health": {"temperature": "float", "heart_rate": "int"}
        }
        assert structure == expected_structure
