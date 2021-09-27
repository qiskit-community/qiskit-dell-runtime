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


from dell_runtime.aerjob import AerJob
from qiskit.providers import BackendV1 as Backend
from qiskit.providers.models import BackendConfiguration
from qiskit.providers.models.backendstatus import BackendStatus
from qiskit.providers import Options
import concurrent.futures
from qiskit.compiler import assemble
from qiskit import Aer
from datetime import datetime

# from . import emulator_job
from .aerjob import AerJob

class EmulatorBackend(Backend):
    def __init__(self, provider):
        default_basic_gates = sorted([
            'u1', 'u2', 'u3', 'u', 'p', 'r', 'rx', 'ry', 'rz', 'id', 'x',
            'y', 'z', 'h', 's', 'sdg', 'sx', 't', 'tdg', 'swap', 'cx',
            'cy', 'cz', 'csx', 'cp', 'cu1', 'cu2', 'cu3', 'rxx', 'ryy',
            'rzz', 'rzx', 'ccx', 'cswap', 'mcx', 'mcy', 'mcz', 'mcsx',
            'mcphase', 'mcu1', 'mcu2', 'mcu3', 'mcrx', 'mcry', 'mcrz',
            'mcr', 'mcswap', 'unitary', 'diagonal', 'multiplexer',
            'initialize', 'delay', 'pauli', 'mcx_gray'
        ])
        supported_instructions = sorted([
            'cx',
            'id',
            'delay',
            'measure',
            'reset',
            'rz',
            'sx',
            'u1',
            'u2',
            'u3',
            'x'])

        default_config = { #https://qiskit.org/documentation/stubs/qiskit.providers.models.BackendConfiguration.html#qiskit.providers.models.BackendConfiguration
            'backend_name': 'emulator',
            'display_name': 'emulator',
            'description': 'Local Emulator',
            'backend_version': "0.1.0",
            'sample_name': 'emulator',
            'n_qubits': 29,
            # TODO: doesn't work for anything other than 1. Need to look at this later
            'n_registers': 1,
            'register_map': None,

            'url': 'https://github.com/Qiskit/qiskit-aer',
            'supported_instructions': supported_instructions,
            'simulator': True,
            'local': True,
            'conditional': True,
            'open_pulse': False,
            'memory': True,
            'configurable': True,
            'credits_required': False,
            'online_date': datetime.now(),
            
            'max_shots': int(1e6),
            'max_experiments': int(1e6),
            'coupling_map': None,
            'basis_gates': default_basic_gates,
            'gates': []
        }
    
        super().__init__(configuration=BackendConfiguration.from_dict(default_config), provider=provider)
    @classmethod
    def _default_options(cls):
        return Options(shots=1, sampler_seed=None)
    
    def run(self, circuit, **run_options):
        # setting options
        qobj = assemble(circuit, self)
        config = qobj.config
        for key, val in run_options.items():
            setattr(config, key, val)
        backend = Aer.get_backend('aer_simulator')
        job = AerJob(self, None, backend._run, qobj)
        job.submit()
        return job

    def status(self):
        # backend_name (str) – The backend’s name
        # backend_version (str) – The backend’s version of the form X.Y.Z
        # operational (bool) – True if the backend is operational
        # pending_jobs (int) – The number of pending jobs on the backend
        # status_msg (str) – The status msg for the backend
        return BackendStatus(
            backend_name=self.name(),
            backend_version="1",
            operational=True,
            pending_jobs=0,
            status_msg="",
        )