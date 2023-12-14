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


from qiskit_aer import Aer

from program import main
from urllib.parse import urljoin
import requests
import os
import sys

from user_messenger_client import RemoteUserMessengerClient

import json
import os
from qiskit.providers.ibmq.runtime.utils import RuntimeDecoder
from dell_runtime import BackendProvider

import logging
import logging.config

logging.config.fileConfig("./logging_config.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

host = os.environ['ORCH_HOST']
job_id = os.environ['JOB_ID']
message_token = os.environ['MESSAGE_TOKEN']


def main_method():
    params = None
    
    params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'params.json')
    with open(params_path, 'r') as params_file:
        params = params_file.read()
    
    inputs = json.loads(params, cls=RuntimeDecoder)

    backend = None
    if 'backend_name' in inputs:
        provider = BackendProvider()
        print(inputs)
        backend_name = inputs['backend_name']
        if 'backend_token' in inputs:
            backend = provider.get_backend(name = backend_name, backend_token=inputs["backend_token"])
        else:
            backend = provider.get_backend(name = backend_name)
        here = os.path.dirname(os.path.realpath(__file__))
        cert_path=os.path.join("/etc/qdr_certs", backend_name+".crt")
        if os.path.isfile(cert_path):
            os.environ["REQUESTS_CA_BUNDLE"]=cert_path
            
    else:
        print("using default backend: " + 'aer_simulator')
        backend = Aer.get_backend('aer_simulator')

    user_messenger = RemoteUserMessengerClient()
    
    try:
        main(backend, user_messenger=user_messenger, **inputs)
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main_method()