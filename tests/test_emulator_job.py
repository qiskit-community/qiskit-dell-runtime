import unittest
from qiskit import QuantumCircuit, execute, transpile
from qiskit_emulator import EmulatorProvider
from qiskit.providers import JobStatus
from time import sleep

class ProviderTest(unittest.TestCase):
    def test_job_submission(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="emulator")
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
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="emulator")
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
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="emulator")
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

    def test_cancel(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        
        backend = provider.get_backend(name="emulator")
        self.assertIsNotNone(backend)

        circ = QuantumCircuit(2)
        circ.h(0)
        circ.cx(0, 1)
        circ.measure_all()

        # Transpile for simulator
        job = backend.run(circ, shots=100000000)

        # Run and get counts
        job.cancel()
        sleep(1.0)
        self.assertEqual(job.status(), '')