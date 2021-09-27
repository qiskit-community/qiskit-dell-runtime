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
from qiskit import QuantumCircuit, execute, transpile
from dell_runtime import BackendProvider
from qiskit.providers import JobStatus
from time import sleep

class ProviderTest(unittest.TestCase):
    def test_job_submission(self):
        provider = BackendProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="aer_simulator")
        self.assertIsNotNone(backend)

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        job = backend.run(qc, shots=1) 
        self.assertIsNotNone(job)
        # self.assertNotEqual(JobStatus.DONE, job.status())
        
        count = 0
        # 5 second
        max = 50 
        while count < max and job.status() != JobStatus.DONE:
            count += 1
            sleep(0.1)
        self.assertEqual(JobStatus.DONE, job.status())

        job.result()


    def test_execute(self):
        provider = BackendProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="aer_simulator")
        self.assertIsNotNone(backend)

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        job = execute(qc, backend, shots=2)
        self.assertIsNotNone(job)

        count = 0
        # 5 second
        max = 50 
        while count < max and job.status() != JobStatus.DONE:
            count += 1
            sleep(0.1)
        self.assertEqual(JobStatus.DONE, job.status())

    def test_get_counts(self):
        provider = BackendProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="aer_simulator")
        self.assertIsNotNone(backend)

        circ = QuantumCircuit(2)
        circ.h(0)
        circ.cx(0, 1)
        circ.measure_all()

        # Transpile for simulator
        circ = transpile(circ, backend)

        # Run and get counts
        result = backend.run(circ).result()
        counts = result.get_counts(circ)
        total = counts.get('11') + counts.get('00')
        self.assertEqual(total, 1024)

