# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# Copyright 2021 Dell (www.dell.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
import os
import json
import logging

# from ..dell_runtime.emulation_executor import EmulationExecutor
from dell_runtime import EmulationExecutor

RUNTIME_PROGRAM = """
import random

from qiskit import transpile
from qiskit.circuit.random import random_circuit

def prepare_circuits(backend):
    circuit = random_circuit(num_qubits=5, depth=4, measure=True,
                            seed=random.randint(0, 1000))
    return transpile(circuit, backend)

def main(backend, user_messenger, **kwargs):
    iterations = kwargs['iterations']
    interim_results = kwargs.pop('interim_results', {})
    final_result = kwargs.pop("final_result", {})
    for it in range(iterations):
        qc = prepare_circuits(backend)
        user_messenger.publish({"iteration": it, "interim_results": interim_results})
        backend.run(qc).result()

    user_messenger.publish(final_result, final=True)
"""
logger = logging.getLogger(__name__)

class EmulationExecutorTest(unittest.TestCase):
    def test_pre_post_run(self):
        try:
            executor = EmulationExecutor(program=None, program_data=(RUNTIME_PROGRAM, "STRING"))
            self.assertIsNotNone(executor)

            executor._pre_run()
            self.assertTrue(os.path.isdir(executor.temp_dir()))

            program_path = os.path.join(executor.temp_dir(), "program.py")
            self.assertTrue(os.path.isfile(program_path))

            with open(program_path, "r") as program_file:
                program_text = program_file.read()
                self.assertEqual(RUNTIME_PROGRAM, program_text)

            executor_path = os.path.join(executor.temp_dir(), "executor.py")
            self.assertTrue(os.path.isfile(executor_path))

        finally:
            executor._post_run()
            self.assertFalse(os.path.isdir(executor.temp_dir()))

        
    


        

        