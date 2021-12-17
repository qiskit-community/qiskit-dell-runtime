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
from dell_runtime import DellRuntimeProvider
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit import QuantumCircuit
import os

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
        # user_messenger.publish({"iteration": it, "interim_results": interim_results})
        backend.run(qc).result()

    user_messenger.publish(final_result, final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "description": "Test program",
    "max_execution_time": 300,
    "backend_requirements": {"min_num_qubits":  5},
    "parameters": [
        {"name": "param1", "description": "Some parameter.",
            "type": "integer", "required": True}
    ],
    "return_values": [
        {"name": "ret_val", "description": "Some return value.", "type": "string"}
    ],
    "interim_results": [
        {"name": "int_res", "description": "Some interim result", "type": "string"},
    ],
    "name": "qiskit-test",
}

# PROGRAM_PREFIX = 'qiskit-test'

class EmulatorRuntimeServiceTest(unittest.TestCase):
    def test_upload(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        proglist = provider.runtime.programs()
        self.assertIsNotNone(proglist[program_id])
        findProgId = False
        if program_id in proglist:
            findProgId = True
        self.assertTrue(findProgId)

    def test_runtime_backends(self):
        provider = DellRuntimeProvider()
        backends = provider.runtime.backends()
        self.assertGreater(len(backends), 1)

    def test_view_program(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        runtime_program = provider.runtime.program(program_id)
        self.assertEqual(runtime_program.description, "Test program")
        self.assertEqual(runtime_program.program_id, program_id)


    def test_run_program(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

        runtime_program = provider.runtime.program(program_id)
        self.assertIsNotNone(runtime_program)
        try:
            job = provider.runtime.run(program_id, options=None, inputs={"iterations": 2})

            result = job.result(timeout=15)
            self.assertIsNotNone(result)
        except Exception:
            self.fail("should pass")


    def test_programs(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        provider.runtime.upload_program("fake-program1", metadata=RUNTIME_PROGRAM_METADATA)
        provider.runtime.upload_program("fake-program2", metadata=RUNTIME_PROGRAM_METADATA)
        programs = provider.runtime.programs()
        self.assertEqual(len(programs), 2)

    
    def test_update_program(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        new_meta = {'description': 'Qiskit Test Update', 'max_execution_time': RUNTIME_PROGRAM_METADATA['max_execution_time']}

        updated = provider.runtime.update_program(program_id, name='Test Update', metadata=new_meta)

        self.assertTrue(updated)

        program2 = provider.runtime.program(program_id, refresh=True)

        self.assertEqual('Qiskit Test Update', program2.description)
        self.assertEqual('Test Update', program2.name)

    def test_pprint_programs(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        pr_id_1 = provider.runtime.upload_program("fake-program1", metadata=RUNTIME_PROGRAM_METADATA)
        import sys
        import io
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        provider.runtime.pprint_programs()
        output = new_stdout.getvalue()
        sys.stdout = old_stdout
        self.assertTrue(output.startswith( 
        '''==================================================
{}:
  Name: {}'''.format(pr_id_1,'qiskit-test')
        ))

    def test_has_service(self):
        provider = DellRuntimeProvider()
        self.assertTrue(provider.has_service('runtime'))
        self.assertFalse(provider.has_service('fake-service'))

    def test_metadata(self):
        provider = DellRuntimeProvider()
        
        pr_id = provider.runtime.upload_program("fake-program1", metadata=RUNTIME_PROGRAM_METADATA)
        program = provider.runtime.program(pr_id)
        self.assertEqual('qiskit-test', program.name)
        self.assertEqual(RUNTIME_PROGRAM_METADATA['description'], program.description)
        self.assertEqual(RUNTIME_PROGRAM_METADATA['max_execution_time'],
                            program.max_execution_time)
        self.assertEqual(RUNTIME_PROGRAM_METADATA['backend_requirements'],
                            program.backend_requirements)

    def test_circuit_runner(self):
        from . import circuit_runner as cr
        try:
            cr.main()
        except Exception as e:
            self.fail("should pass")

    def test_dir_circuit_runner(self):
        from . import dir_circuit_runner as dcr
        try:
            dcr.main()
        except Exception as e:
            self.fail("should pass")

    def test_upload_file(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        here = os.path.dirname(os.path.realpath(__file__))
        program_id = provider.runtime.upload_program(here + "/dirtest/", metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

        runtime_program = provider.runtime.program(program_id)
        self.assertIsNotNone(runtime_program)
        try:
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            qc.measure([0, 1], [0, 1])

            program_inputs = {
                'circuits': qc,
            }

            job = provider.runtime.run(program_id, options=None, inputs=program_inputs)

            result = job.result(timeout=15)
            self.assertIsNotNone(result)
        except Exception:
            self.fail("should pass")

    def test_reserved_names(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        try:
            here = os.path.dirname(os.path.realpath(__file__))
            program_id = provider.runtime.upload_program(here + "/dirfail/", metadata=RUNTIME_PROGRAM_METADATA)
            self.fail("Should not allow upload")
        except Exception:
            self.assertTrue(True)

    def test_delete_program(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        prog_list = provider.runtime.programs(refresh=False)

        self.assertTrue(len(prog_list) >= 1)

        deleted = provider.runtime.delete_program(program_id)

        self.assertTrue(deleted)

        new_prog_list = provider.runtime.programs(refresh=True)
        
        self.assertGreater(len(prog_list), len(new_prog_list))