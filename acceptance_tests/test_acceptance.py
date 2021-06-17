from qiskit_emulator.emulator_runtime_job import EmulatorRuntimeJob
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
    print("job complete successfully")
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
        self.assertIsNotNone(proglist[program_id])
        findProgId = False
        logger.debug(proglist)
        if program_id in proglist:
            findProgId = True
        self.assertTrue(findProgId)

    def test_view_program(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        runtime_program = provider.runtime.program(program_id)
        self.assertEqual(runtime_program.description, "Qiskit test program")
        self.assertEqual(runtime_program.program_id, program_id)

    def test_view_program_refresh(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        prog_list = provider.runtime.programs(refresh=False)

        self.assertTrue(len(prog_list) >= 1)

        new_program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        new_prog_list = provider.runtime.programs(refresh=False)
        
        self.assertEqual(len(prog_list), len(new_prog_list))

        newnew_prog_list = provider.runtime.programs(refresh=True)

        self.assertGreater(len(newnew_prog_list), len(prog_list))

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

        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        self.assertEqual(job.host, ACCEPTANCE_URL)
    
    def test_get_results(self):
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
        results = job.result()
        self.assertEqual('aer_simulator', results['backend_name'])