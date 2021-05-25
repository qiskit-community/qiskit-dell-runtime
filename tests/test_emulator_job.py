import unittest
from qiskit import QuantumCircuit, execute
from qiskit_emulator import EmulatorProvider
from qiskit.providers import JobStatus

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
        self.assertTrue(job.status() == JobStatus.DONE)

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
        self.assertTrue(job.status() == JobStatus.DONE)
