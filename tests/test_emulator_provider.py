import unittest
from qiskit_emulator import EmulatorProvider

class ProviderTest(unittest.TestCase):
    def test_new_provider(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
