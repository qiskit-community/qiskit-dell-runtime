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


from dell_runtime.emulator_runtime_job import EmulatorRuntimeJob
import unittest
from qiskit import QuantumCircuit, execute, transpile
from dell_runtime import DellRuntimeProvider
from qiskit.providers import JobStatus
from time import sleep
import os
import logging
import json
import requests
from urllib.parse import urljoin
from qiskit.providers.ibmq.runtime.utils import RuntimeDecoder

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

VQE_PROGRAM = """
from qiskit import Aer
from qiskit.opflow import X, Z, I
from qiskit.utils import QuantumInstance, algorithm_globals
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.algorithms import VQE
from qiskit.algorithms.optimizers import SLSQP
from qiskit.circuit.library import TwoLocal
import json

def result_to_jsonstr(res):
    resd = {}
    resd['eigenvalue'] = res.eigenvalue
    resd['opt_time'] = res.optimizer_time
    return json.dumps(resd, cls=RuntimeEncoder)

def main(backend, user_messenger, **kwargs):
    H2_op = (-1.052373245772859 * I ^ I) + \
            (0.39793742484318045 * I ^ Z) + \
            (-0.39793742484318045 * Z ^ I) + \
            (-0.01128010425623538 * Z ^ Z) + \
            (0.18093119978423156 * X ^ X)

#     seed = random.randint(0, 1000)
#     print(seed)
    seed = kwargs['seed']
    algorithm_globals.random_seed = seed
    qi = QuantumInstance(backend, seed_transpiler=seed, seed_simulator=seed, shots=kwargs['shots'])
    ansatz = TwoLocal(rotation_blocks='ry', entanglement_blocks='cz')
    slsqp = SLSQP(maxiter=1000)
    vqe = VQE(ansatz, optimizer=slsqp, quantum_instance=qi, include_custom=kwargs['include_custom'])
    result = vqe.compute_minimum_eigenvalue(operator=H2_op)

    result = result_to_jsonstr(result)

    user_messenger.publish(result, final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

PROGRAM_PREFIX = 'qiskit-test'

SERVER_URL = os.getenv('SERVER_URL')

class AcceptanceTest(unittest.TestCase):
    def test_circuit_runner(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        # program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        
    def test_remote_fail(self):
        exc = False
        try:
            provider = DellRuntimeProvider()
            provider.remote("http://thisurldoesntexist.com")
        except Exception:
            exc = True
        self.assertTrue(exc)

    def test_upload(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        proglist = provider.runtime.programs()
        self.assertIsNotNone(proglist[program_id])
        findProgId = False
        logger.debug(proglist)
        if program_id in proglist:
            findProgId = True
        self.assertTrue(findProgId)

    def test_view_program(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        runtime_program = provider.runtime.program(program_id)
        self.assertEqual(runtime_program.description, "Qiskit test program")
        self.assertEqual(runtime_program.program_id, program_id)

    def test_view_program_refresh(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        prog_list = provider.runtime.programs(refresh=False)

        self.assertTrue(len(prog_list) >= 1)

        new_program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        new_prog_list = provider.runtime.programs(refresh=False)
        
        self.assertEqual(len(prog_list), len(new_prog_list))

        newnew_prog_list = provider.runtime.programs(refresh=True)

        self.assertGreater(len(newnew_prog_list), len(prog_list))

    def test_run_program(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
        self.assertEqual(job.host, SERVER_URL)
    
    def test_get_results(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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
        response = job.result(timeout=180)
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
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        prog_list = provider.runtime.programs(refresh=False)

        self.assertTrue(len(prog_list) >= 1)

        deleted = provider.runtime.delete_program(program_id)

        self.assertTrue(deleted)

        new_prog_list = provider.runtime.programs(refresh=True)
        
        self.assertGreater(len(prog_list), len(new_prog_list))

    def test_update_program(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        new_meta = {'description': 'Qiskit Test Update', 'max_execution_time': RUNTIME_PROGRAM_METADATA['max_execution_time']}

        updated = provider.runtime.update_program(program_id, name='Test Update', metadata=new_meta)

        self.assertTrue(updated)

        program2 = provider.runtime.program(program_id, refresh=True)

        self.assertEqual('Qiskit Test Update', program2.description)
        self.assertEqual('Test Update', program2.name)

    def test_intermittent_results(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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

    def test_get_status(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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
        correct_status = status == "Creating" or status == "Pending" or status == "Running"
        self.assertTrue(correct_status)
        job.result(timeout=120)
        status = job.status()
        self.assertEqual(status, "Completed")

    def test_get_failed_status(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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
        self.assertTrue(status == "Creating" or status == "Pending")
        
        while status == "Running" or status == "Creating" or status == "Pending":
            status = job.status()
            sleep(5)

        self.assertEqual(status, "Failed")

    def test_cancel_job(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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
        res = job.cancel()
        self.assertTrue(res)

        status = job.status()
        self.assertEqual(status, "Canceled")
    def test_pprint_programs(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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
        print(output)
        self.assertTrue(
        '''==================================================
{}:
  Name: {}'''.format(pr_id_1,pr_id_1)
         in output)


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
        provider.remote(SERVER_URL)

        program_id = provider.runtime.upload_program(here + "/program.py", metadata=RUNTIME_PROGRAM_METADATA)
        self.assertGreaterEqual(len(provider.runtime.programs()), 1)

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

            result = job.result(timeout=90)
            self.assertIsNotNone(result)

        except Exception:
            self.fail("should pass")

    def test_reserved_names(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)

        try:
            here = os.path.dirname(os.path.realpath(__file__))
            program_id = provider.runtime.upload_program(here + "/dirfail/", metadata=RUNTIME_PROGRAM_METADATA)
            self.fail("Should not allow upload")
        except Exception:
            self.assertTrue(True)

    def test_large_directory(self):
        
        provider = DellRuntimeProvider()

        provider.remote(SERVER_URL)
        here = os.path.dirname(os.path.realpath(__file__))
        program_id = provider.runtime.upload_program(here + "/qkad", metadata=RUNTIME_PROGRAM_METADATA)

        job = provider.runtime.run(program_id, options=None, inputs={'garbage': 'nonsense'})

        res = job.result(timeout=600)
        self.assertTrue("aligned_kernel_parameters" in res)
        self.assertTrue("aligned_kernel_matrix" in res)

    def test_callback_function(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
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
        
        print(output)
        self.assertTrue("{'results': 'intermittently'}" in output)
    
    def test_reconnect(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        program_inputs = {
            'circuits': qc,
        }

        del(provider)

        # delete session and sign back in via SSO
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)

        job = provider.runtime.run(program_id, options=None, inputs=program_inputs)

        response = job.result(timeout=120)
        logger.debug("through")


        results = response['results'][0]

        self.assertIsNotNone(results)
        self.assertTrue(results['success'])
        self.assertTrue(results['success'])
        self.assertEqual("DONE", results['status'])

        shots = results['shots']
        count = results['data']['counts']['0x0']

        self.assertGreater(count, (0.45 * shots))
        self.assertLess(count, (0.55 * shots))

    def test_data_security(self):
        provider = DellRuntimeProvider()
        provider.remote(SERVER_URL)
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)

        url = urljoin(SERVER_URL, f'/program/{program_id}/data')
        res = requests.get(url)
        
        self.assertEqual(res.text, "Id and token not presented")
        self.assertEqual(res.status_code, 401)

    def test_block_nonsso_on_sso_server(self):
        res = requests.get(urljoin(SERVER_URL, '/sso_enabled'))
        sso_enabled = json.loads(res.text)
        if sso_enabled:
            url = urljoin(SERVER_URL, '/new_user')
            res = requests.get(url)
            self.assertEqual(res.status_code, 401)

            url = urljoin(SERVER_URL, '/existing_user/2187121124')
            res = requests.get(url)
            self.assertEqual(res.status_code, 401) 

    def test_block_sso_on_nonsso_server(self):
        res = requests.get(urljoin(SERVER_URL, '/sso_enabled'))
        sso_enabled = json.loads(res.text)
        if not sso_enabled:
            url = urljoin(SERVER_URL, '/login')
            res = requests.get(url)
            self.assertEqual(res.status_code, 401)

            url = urljoin(SERVER_URL, '/authenticate')
            res = requests.post(url)
            self.assertEqual(res.status_code, 401)


            url = urljoin(SERVER_URL, '/tokeninfo/109129612')
            res = requests.get(url)
            self.assertEqual(res.status_code, 401)


            url = urljoin(SERVER_URL, '/callback')
            res = requests.get(url)
            self.assertEqual(res.status_code, 401)

    def test_vqe_emulation(self):
        vqe_inputs = {
            'shots': 2,
            'seed': 10,
            'include_custom': True
        }

        provider = DellRuntimeProvider()
        provider.remote(os.getenv("SERVER_URL"))

        program_id = provider.runtime.upload_program(VQE_PROGRAM)

        job = provider.runtime.run(
            program_id=program_id,
            inputs=vqe_inputs,
            options=None)
            
        # result = job.result()

        result = job.result(timeout=100)
        
        result = json.loads(job.result(), cls=RuntimeDecoder)

        self.assertEqual(-1.8572748921516753, result['eigenvalue'])
        self.assertLessEqual(result['opt_time'], 0.4)