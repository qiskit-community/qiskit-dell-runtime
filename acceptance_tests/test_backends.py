from dell_runtime import DellRuntimeProvider
from dell_runtime.emulator_runtime_job import EmulatorRuntimeJob
import unittest
from qiskit import QuantumCircuit, execute, transpile
from qiskit.providers import JobStatus
import unittest
from urllib.parse import urljoin
import os, requests
import json

SERVER_URL = os.getenv('SERVER_URL')

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

RUNTIME_PROGRAM_METADATA = {
        "max_execution_time": 600,
        "description": "Qiskit test program"
}

class BackendTest(unittest.TestCase):
    def test_circuit_runner(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        backends = provider.runtime.backends()
        self.assertGreater(len(backends), 1)

    def test_run_with_backend(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
            'backend_name':"emulator",
        }

        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        self.assertEqual(job.host, SERVER_URL) 
