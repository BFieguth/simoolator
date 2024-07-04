from cython.parallel import prange
import cython
from libc.stdlib cimport malloc, free
import numpy as np
cimport numpy as np
from cow import Cow
from threading import Thread

cdef class ParallelExecutor:
    def __init__(self, list cows_in_herd):
        self.cows_in_herd = cows_in_herd

    def _run_model(self, object cow, object model_function, dict input_mapping):
        cow.run_model(model_function, input_mapping)

    def execute_models(self, object model_function, dict input_mapping):
        threads = []
        for cow in self.cows_in_herd:
            thread = Thread(target=self._run_model, args=(cow, model_function, input_mapping))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
