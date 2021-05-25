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

        # TODO: Need to relook at this later
        self.assertEqual(54, len(backend_config.basis_gates))

        self.assertTrue(backend_config.local)
        self.assertTrue(backend_config.simulator)

        self.assertTrue(backend_config.conditional)

        # TODO: Support OpenPulse later!
        self.assertFalse(backend_config.open_pulse)

        self.assertTrue(backend_config.memory)

        # TODO: May need to change this
        self.assertEqual(int(1e6), backend_config.max_shots)

        # TODO: May need to change this later
        self.assertIsNone(backend_config.coupling_map)
        
        self.assertIsNotNone(backend_config.supported_instructions)
        self.assertEqual(11, len(backend_config.supported_instructions))

        # TODO: Support this feature later
        self.assertFalse(backend_config.dynamic_reprate_enabled)

        self.assertEqual(int(1e6), backend_config.max_experiments)
        self.assertEqual('emulator', backend_config.sample_name)

        self.assertEqual(1, backend_config.n_registers)

        # TODO: Need to look at register map later. Setting to None does not work
        # self.assertIsNone(backend_config.register_map)

        self.assertTrue(backend_config.configurable)
        self.assertFalse(backend_config.credits_required)

        self.assertIsNotNone(backend_config.online_date)
        self.assertEqual('emulator', backend_config.display_name)
        self.assertEqual('Local Emulator', backend_config.description)
        
        # TODO: add tags dt dtm processor_type later


        
