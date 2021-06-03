import unittest
from qiskit_emulator import LocalUserMessenger, LocalUserMessengerClient
from qiskit_emulator import EmulatorRuntimeJob

class EmulatorRuntimeJobTest(unittest.TestCase):
    def test_emulator_runtime_job(self):
        job = EmulatorRuntimeJob()
        self.assertIsNotNone(job)
        messenger = LocalUserMessenger()
        self.assertIsNotNone(messenger)
        job.user_messenger = messenger
        self.assertIsNotNone(job.user_messenger)
