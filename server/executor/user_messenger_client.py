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


from typing import Any, Type
import json
from qiskit.providers.ibmq.runtime import UserMessenger, RuntimeEncoder
import requests
from urllib.parse import urljoin
import os

class RemoteUserMessengerClient(UserMessenger):
    def __init__(self):
        self.host = os.environ['ORCH_HOST']
        self.job_id = os.environ['JOB_ID']
        self._session = requests.Session()
        url = urljoin(self.host, f'/register_messenger/{self.job_id}')
        res = self._session.get(url, data={'token': os.environ["MESSAGE_TOKEN"]})
        if res.status_code != 200:
            raise Exception(f"failure in messenger registration: {res.text}")

    def publish(
            self,
            message: Any,
            encoder: Type[json.JSONEncoder] = RuntimeEncoder,
            final: bool = False
    ):  
    
        str_msg = json.dumps({"final": final, "message": message}, cls=encoder)
        url = urljoin(self.host, f'job/{self.job_id}/message')
        req = self._session.post(url, json=str_msg)
        if req.status_code != 200:
            raise (f'Error POST {url}: {req.status_code}')
