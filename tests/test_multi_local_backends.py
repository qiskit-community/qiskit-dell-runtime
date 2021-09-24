from dell_runtime import DellRuntimeProvider
import unittest
from qiskit import QuantumCircuit, execute, transpile
from time import sleep
import logging

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

class MultiLocalBackendTest(unittest.TestCase):

    def test_get_results_emulator_backend(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
            'backend_name': 'emulator'
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

    def test_get_results_aer_backend(self):
        provider = DellRuntimeProvider()
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
            'backend_name': 'aer_simulator'
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