import unittest
from qiskit_emulator import RuntimeEmulatorProvider

class ProviderTest(unittest.TestCase):
    def test_new_provider(self):
        provider = RuntimeEmulatorProvider()
        self.assertIsNotNone(provider)
