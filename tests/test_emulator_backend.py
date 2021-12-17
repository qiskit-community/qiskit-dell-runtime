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
from dell_runtime import BackendProvider

class ProviderTest(unittest.TestCase):
    def test_get_backend(self):
        provider = BackendProvider()
        self.assertGreater(len(provider.backends()), 1)

        backend = provider.get_backend(name="aer_simulator")
        self.assertIsNotNone(backend)

    def test_backend_configuration(self):
        # ENSURE it matches with https://qiskit.org/documentation/stubs/qiskit.providers.models.BackendConfiguration.html
        provider = BackendProvider()
        self.assertGreater(len(provider.backends()), 1)

        backend = provider.get_backend(name="aer_simulator")
        self.assertIsNotNone(backend)

        backend_config = backend.configuration()
        self.assertIsNotNone(backend_config)

        self.assertEqual("aer_simulator", backend_config.backend_name)
        # self.assertEqual("0.1.0", backend_config.backend_version)
        self.assertGreater(backend_config.n_qubits, 25)

        # TODO: Need to relook at this later
        self.assertEqual(83, len(backend_config.basis_gates))

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
        
        # self.assertIsNotNone(backend_config.supported_instructions)
        # self.assertEqual(11, len(backend_config.supported_instructions))

        # TODO: Support this feature later
        self.assertFalse(backend_config.dynamic_reprate_enabled)

        # self.assertEqual(int(1e6), backend_config.max_experiments)
        # self.assertEqual('emulator', backend_config.sample_name)

        # self.assertEqual(1, backend_config.n_registers)

        # TODO: Need to look at register map later. Setting to None does not work
        # self.assertIsNone(backend_config.register_map)

        # self.assertTrue(backend_config.configurable)
        # self.assertFalse(backend_config.credits_required)

        # self.assertIsNotNone(backend_config.online_date)
        # self.assertEqual('emulator', backend_config.display_name)
        # self.assertEqual('Local Emulator', backend_config.description)
        self.assertIsNotNone(backend_config.description)
        
        # TODO: add tags dt dtm processor_type later



        
