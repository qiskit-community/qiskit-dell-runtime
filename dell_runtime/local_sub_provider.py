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


from qiskit import Aer
from qiskit.providers.exceptions import QiskitBackendNotFoundError
# from qiskit import IBMQ

from .emulator_backend import EmulatorBackend

class LocalSubProviderManager():
    def __init__(self, provider):
        self._provider = provider
        self._init_backends()
            
    def _init_backends(self):
        self._backends = [Aer.get_backend('aer_simulator')]
        self._backends.append(EmulatorBackend(self._provider))

        # for sub_provider in self.sub_providers:
            # self._backends += sub_provider.backends()
        
        self._backends_by_name = {}
        for backend in self._backends:
            self._backends_by_name[backend.name()] = backend


    def backends(self):
        return self._backends

    def get_backend(self, name=None, **kwargs):
        if name not in self._backends_by_name:
            raise QiskitBackendNotFoundError("No backend matches criteria.")
        else:
            return self._backends_by_name[name]



    
