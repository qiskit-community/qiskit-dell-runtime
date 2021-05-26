import unittest
from qiskit_emulator import EmulatorProvider

class ProviderTest(unittest.TestCase):
    def test_new_provider(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)

    def test_backends(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)

        self.assertEqual(1, len(provider.backends()))

    # def test_runtime_supported(self):
    #     provider = EmulatorProvider()
    #     self.assertIsNotNone(provider)

    #     self.assertTrue(provider.has_service('runtime'))
