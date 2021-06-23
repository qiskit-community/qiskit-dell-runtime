from typing import Any, Type
from qiskit.providers.ibmq.runtime import UserMessenger, RuntimeEncoder
import threading
import json
import socket
import logging

logger = logging.getLogger(__name__)

# class LocalUserMessenger():
#     def __init__(self):
#         self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self._sock.bind(('localhost', 0))
#         self._run = False
#         self._thread = None
#         self._message_log = []

#     def port(self):
#         return self._sock.getsockname()[1]

#     def _process(self):
#         logging.debug(f"starting to listen to port {self.port()}")
#         self._sock.listen(1)

#         conn, addr = self._sock.accept()
#         logging.debug(f"accepted client connection from {addr}")
#         self._run = True
#         with conn:
#             while self._run:
#                 # TODO: loop here...
#                 data = conn.recv(4096)
#                 if not data:
#                     break
#                 else:
#                     data_obj = json.loads(data.decode("utf-8"))
#                     message = data_obj["message"]
#                     print(f"MESSENGER RECEIVED: {message}")
#                     self._message_log.append(message)
#                     logging.debug(f"MESSENGER RECEIVED: {message}")

#                     # Close messenger if final publish
#                     if data_obj["isFinal"]:
#                         print(data_obj)
#                         self.close()

#     def message_log(self):
#         return self._message_log

#     def listen(self):
#         self._thread = threading.Thread(target = self._process)
#         self._thread.start()
        
#     def close(self):
#         self._run = False
#         self._sock.close()

#     def isClosed(self):
#         if self._sock.fileno() == -1:
#             return True
#         return False

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
        # TODO: use provided (if any) encoder
        # if encoder is not None:
        #     str_messenge = encoder.dumps()

        jsonMessage = {
            "message": message,
            "final": final
        }
        
        str_message = json.dumps(jsonMessage, cls=encoder)
        self._sock.sendall(bytes(str_message + '\u0004', 'utf-8'))

        # Close connection if final message
        if final:
            self._sock.close()
