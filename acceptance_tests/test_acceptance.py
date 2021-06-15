import unittest
from qiskit import QuantumCircuit, execute, transpile
from qiskit_emulator import EmulatorProvider
from qiskit.providers import JobStatus
from time import sleep
import os
import logging

logger = logging.getLogger(__name__)

RUNTIME_PROGRAM = """
from qiskit.compiler import transpile, schedule


def main(
    backend,
    user_messenger,
    circuits,
    **kwargs,
):
    circuits = transpile(
        circuits,
    )

    if not isinstance(circuits, list):
        circuits = [circuits]

    # Compute raw results
    result = backend.run(circuits, **kwargs).result()

    user_messenger.publish(result.to_dict(), final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

PROGRAM_PREFIX = 'qiskit-test'

ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')

class AcceptanceTest(unittest.TestCase):
    def test_circuit_runner(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        # program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        
    def test_remote_fail(self):
        exc = False
        try:
            provider = EmulatorProvider()
            provider.remote("http://thisurldoesntexist.com")
        except Exception:
            exc = True
        self.assertTrue(exc)

    def test_upload(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        proglist = provider.runtime.programs()
        self.assertIsNotNone(proglist[0])
        findProgId = False
        logger.debug(proglist)
        for prog in proglist:
            if prog.program_id == program_id:
                findProgId = True
        self.assertTrue(findProgId)

    def test_run_program(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        runtime_program = provider.runtime.program(program_id)
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)