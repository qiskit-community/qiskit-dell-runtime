from qiskit_emulator import EmulatorProvider
import unittest
from urllib.parse import urljoin
import os, requests
import json

ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')

class BackendTest(unittest.TestCase):
    def test_circuit_runner(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        backends = provider.runtime.backends()
        self.assertGreater(len(backends), 1)

    def test_run_with_backend(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
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
        self.assertEqual(job.host, ACCEPTANCE_URL) 

    # def test_ionq_results(self):
    #     provider = EmulatorProvider()
    #     provider.remote(ACCEPTANCE_URL)
    #     program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


    #     qc = QuantumCircuit(2, 2)
    #     qc.h(0)
    #     qc.cx(0, 1)
    #     qc.measure([0, 1], [0, 1])

    #     program_inputs = {
    #         'circuits': qc,
    #         'backend_name': 'ionq_simulator',
    #         'backend_token': os.environ["IONQ_TOKEN"]
    #     }

    #     # runtime_program = provider.runtime.program(program_id)
    #     job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
    #     response = job.result(timeout=180)
    #     # print(json.dumps(results))
    #     # results['results'] = json.loads(results['results'])

    #     results = response['results'][0]

    #     self.assertIsNotNone(results)
    #     self.assertTrue(results['success'])

    #     shots = results['shots']
    #     count = results['data']['counts']['0x0']

    #     self.assertGreater(count, (0.45 * shots))
    #     self.assertLess(count, (0.55 * shots))
