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
from qiskit.providers.ibmq.runtime import UserMessenger, RuntimeEncoder
import threading
import json
import socket
import logging

logger = logging.getLogger(__name__)

class LocalUserMessengerClient(UserMessenger):
    def __init__(self, port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(f"client connecting port {port}")
        self._sock.connect(('localhost', port))

    def publish(
            self,
            message: Any,
            encoder: Type[json.JSONEncoder] = RuntimeEncoder,
            final: bool = False
    ) -> None:

        jsonMessage = {
            "message": message,
            "final": final
        }
        
        str_message = json.dumps(jsonMessage, cls=encoder)
        self._sock.sendall(bytes(str_message + '\u0004', 'utf-8'))

        # Close connection if final message
        if final:
            self._sock.close()
