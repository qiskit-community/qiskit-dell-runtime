import unittest
from qiskit_emulator import EmulatorProvider

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

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

PROGRAM_PREFIX = 'qiskit-test'

class EmulatorRuntimeServiceTest(unittest.TestCase):

    def test_upload_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        self.assertEqual(0, len(provider.runtime.programs()))
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

    def test_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

        runtime_program = provider.runtime.program('fake_id')
        self.assertIsNone(runtime_program)

        runtime_program = provider.runtime.program(program_id)
        self.assertIsNotNone(runtime_program)

    def test_run_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

        runtime_program = provider.runtime.program(program_id)
        self.assertIsNotNone(runtime_program)

        provider.runtime.run(program_id, options=None, inputs=None)


    def test_pprint_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        provider.runtime.pprint_programs()
