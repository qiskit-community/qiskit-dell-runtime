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
