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


from dell_runtime import DellRuntimeProvider
import unittest
from dell_runtime import LocalUserMessengerClient
from dell_runtime import EmulatorRuntimeJob, EmulationExecutor
from qiskit import QuantumCircuit, execute, transpile
from time import sleep
import logging

# RUNTIME_PROGRAM = """
# import random

# from qiskit import transpile
# from qiskit.circuit.random import random_circuit

# def prepare_circuits(backend):
#     circuit = random_circuit(num_qubits=5, depth=4, measure=True,
#                             seed=random.randint(0, 1000))
#     return transpile(circuit, backend)

# def main(backend, user_messenger, **kwargs):
#     iterations = kwargs['iterations']
#     interim_results = kwargs.pop('interim_results', {})
#     final_result = kwargs.pop("final_result", {})
#     for it in range(iterations):
#         qc = prepare_circuits(backend)
#         user_messenger.publish({"iteration": it, "interim_results": interim_results})
#         backend.run(qc).result()

#     user_messenger.publish(final_result, final=True)
# """
RUNTIME_PROGRAM = """
from qiskit.compiler import transpile, schedule


def main(
    backend,
    user_messenger,
    circuits,
    **kwargs,
):

    user_messenger.publish({'results': 'intermittently'})

    circuits = transpile(
        circuits,
    )

    if not isinstance(circuits, list):
        circuits = [circuits]

    # Compute raw results
    result = backend.run(circuits, **kwargs).result()

    user_messenger.publish({'results': 'finally'})
    user_messenger.publish(result.to_dict(), final=True)
    print("job complete successfully")
"""

FAIL_PROGRAM = """
from qiskit.compiler import transpile, schedule


def main(
    backend,
    user_messenger,
    circuits,
    **kwargs,
):

    raise Exception('test failure')
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

logger = logging.getLogger(__name__)

class EmulatorRuntimeJobTest(unittest.TestCase):
    def test_multiple_runtime_jobs(self):
        executor = EmulationExecutor(program=None, program_data=(RUNTIME_PROGRAM, "STRING"), inputs = { "iterations": 2 })
        executor2 = EmulationExecutor(program=None, program_data=(RUNTIME_PROGRAM, "STRING"), inputs = { "iterations": 2 })
        executor3 = EmulationExecutor(program=None, program_data=(RUNTIME_PROGRAM, "STRING"), inputs = { "iterations": 2 })
        self.assertIsNotNone(executor)
        job = EmulatorRuntimeJob("1", None, executor=executor)
        job2 = EmulatorRuntimeJob("1", None, executor=executor2)
        job3 = EmulatorRuntimeJob("1", None, executor=executor3)
        sleep(1)        
        self.assertIsNotNone(job)
        job.cancel()
        job2.cancel()
        job3.cancel()
        # pdb.set_trace()
        sleep(1)
        status = job.status()
        self.assertEqual(status, "Canceled")

    def test_intermittent_results(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        # runtime_program = provider.runtime.program(program_id)
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        
        result = job.result(timeout=15)
        messages = job.get_unread_messages()
        logger.debug(f'unread messages {messages}')
            
        self.assertEqual(len(messages), 2)
        self.assertEqual("intermittently", messages[0]['results'])
        self.assertEqual("finally", messages[1]['results'])

        messages = job.get_unread_messages()
        
        self.assertEqual(0, len(messages))

            
    def test_get_results(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        response = job.result(timeout=15)

        results = response['results'][0]

        self.assertIsNotNone(results)
        self.assertTrue(results['success'])
        self.assertTrue(results['success'])
        self.assertEqual("DONE", results['status'])

        shots = results['shots']
        count = results['data']['counts']['0x0']

        self.assertGreater(count, (0.45 * shots))
        self.assertLess(count, (0.55 * shots))

    

    def test_get_status(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        # runtime_program = provider.runtime.program(program_id)
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        status = job.status()
        correct_status = status == "Creating" or status == "Running"
        self.assertTrue(correct_status)
        job.result(timeout=15)
        status = job.status()

        max_try = 50
        attempt = 0
        while (status == "Creating" or status == "Running") and attempt < max_try:
            sleep(0.1)
            attempt += 1
            status = job.status()
            
        self.assertEqual(status, "Completed")

    def test_get_failed_status(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(FAIL_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        status = job.status()
        self.assertEqual(status, "Creating")
        
        max_try = 50
        attempt = 0
        while (status == "Creating" or status == "Running") and attempt < max_try:
            sleep(0.1)
            attempt += 1
            status = job.status()

        self.assertEqual(status, "Failed")

    def test_cancel_job(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        # runtime_program = provider.runtime.program(program_id)
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        sleep(1)

        res = job.cancel()
        self.assertTrue(res)

        status = job.status()
        self.assertEqual(status, "Canceled")

    def test_callback_function(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        
        import sys
        import io
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs,callback=print)
        result =job.result(timeout=120)
        output = new_stdout.getvalue()
        sys.stdout = old_stdout
        
        self.assertTrue("{'results': 'intermittently'}"
         in output)
