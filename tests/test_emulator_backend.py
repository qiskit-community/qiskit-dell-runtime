import unittest
from qiskit_emulator import EmulatorProvider

class ProviderTest(unittest.TestCase):
    def test_get_backend(self):
        provider = EmulatorProvider()
        self.assertEqual(1, len(provider.backends()))

        backend = provider.get_backend(name="emulator")
        self.assertIsNotNone(backend)

    def test_backend_configuration(self):
        # ENSURE it matches with https://qiskit.org/documentation/stubs/qiskit.providers.models.BackendConfiguration.html
        provider = EmulatorProvider()
        self.assertEqual(1, len(provider.backends()))

        backend = provider.get_backend(name="emulator")
        self.assertIsNotNone(backend)

        backend_config = backend.configuration()
        self.assertIsNotNone(backend_config)

        self.assertEqual("emulator", backend_config.backend_name)
        self.assertEqual("0.1.0", backend_config.backend_version)
        self.assertEqual(29, backend_config.n_qubits)

        # TODO: Support OpenPulse later!
        self.assertFalse(backend_config.open_pulse)
        self.assertTrue(backend_config.simulator)


        self.assertTrue(backend_config.local)
