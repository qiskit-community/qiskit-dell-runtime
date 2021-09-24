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
