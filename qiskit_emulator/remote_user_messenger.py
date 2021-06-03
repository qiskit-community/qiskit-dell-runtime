from typing import Any, Type
import json
from qiskit.providers.ibmq.runtime import UserMessenger, RuntimeEncoder

class RemoteUserMessengerClient(UserMessenger):
    def publish(
            self,
            message: Any,
            encoder: Type[json.JSONEncoder] = RuntimeEncoder,
            final: bool = False
    ) -> None:
        return None