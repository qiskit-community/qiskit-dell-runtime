from qiskit_emulator.emulator_runtime_job import EmulatorRuntimeJob
import unittest
from qiskit import QuantumCircuit, execute, transpile
from qiskit_emulator import EmulatorProvider
from qiskit.providers import JobStatus
from time import sleep
import os
import logging
import json

logger = logging.getLogger(__name__)

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

        # runtime_program = provider.runtime.program(program_id)
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        response = job.result(timeout=120)
        logger.debug("through")
        # print(json.dumps(results))
        # results['results'] = json.loads(results['results'])

        results = response['results'][0]

        self.assertIsNotNone(results)
        self.assertTrue(results['success'])
        self.assertTrue(results['success'])
        self.assertEqual("DONE", results['status'])

        shots = results['shots']
        count = results['data']['counts']['0x0']

        self.assertGreater(count, (0.45 * shots))
        self.assertLess(count, (0.55 * shots))

    def test_delete_program(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        prog_list = provider.runtime.programs(refresh=False)

        self.assertTrue(len(prog_list) >= 1)

        deleted = provider.runtime.delete_program(program_id)

        self.assertTrue(deleted)

        new_prog_list = provider.runtime.programs(refresh=True)
        
        self.assertGreater(len(prog_list), len(new_prog_list))

    def test_update_program(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        new_meta = {'description': 'Qiskit Test Update', 'max_execution_time': RUNTIME_PROGRAM_METADATA['max_execution_time']}

        updated = provider.runtime.update_program(program_id, name='Test Update', metadata=new_meta)

        self.assertTrue(updated)

        program2 = provider.runtime.program(program_id, refresh=True)

        self.assertEqual('Qiskit Test Update', program2.description)
        self.assertEqual('Test Update', program2.name)

    def test_intermittent_results(self):
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

        # runtime_program = provider.runtime.program(program_id)
        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        
        result = job.result(timeout=120)
        messages = job.get_unread_messages()
        logger.debug(f'unread messages {messages}')
            
        self.assertEqual(len(messages), 2)
        self.assertEqual("intermittently", messages[0]['results'])
        self.assertEqual("finally", messages[1]['results'])

        messages = job.get_unread_messages()
        
        self.assertEqual(0, len(messages))