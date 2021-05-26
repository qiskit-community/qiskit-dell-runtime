import unittest
from qiskit_emulator import EmulatorProvider

class ProviderTest(unittest.TestCase):
    def test_pprint_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        provider.runtime.pprint_programs()
