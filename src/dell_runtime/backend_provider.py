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


import logging
import os

from qiskit.providers import ProviderV1 as Provider

logger = logging.getLogger(__name__)

from .local_sub_provider import LocalSubProviderManager

class BackendProvider(Provider):

    def __init__(self):
        super().__init__()
        self.sub_provider_manager = LocalSubProviderManager(self)
        self.services = {
        }

    def get_backend(self, name=None, **kwargs):
        return self.sub_provider_manager.get_backend(name=name, **kwargs)
        
    def backends(self, name=None, **kwargs):
        return self.sub_provider_manager.backends()

