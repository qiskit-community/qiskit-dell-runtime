from typing import Any, Type
import json
from qiskit.providers.ibmq.runtime import UserMessenger, RuntimeEncoder
# from kafka import KafkaProducer
import requests
from urllib.parse import urljoin
import os

class RemoteUserMessengerClient(UserMessenger):
    def __init__(self):
        self.host = os.environ['ORCH_HOST']
        self.job_id = os.environ['JOB_ID']

    def publish(
            self,
            message: Any,
            encoder: Type[json.JSONEncoder] = RuntimeEncoder,
            final: bool = False
    ):  
    
        str_msg = json.dumps({"final": final, "message": message}, cls=encoder)
        url = urljoin(self.host, f'job/{self.job_id}/message')
        req = requests.post(url, str_msg)
        if req.status_code != 200:
            raise (f'Error POST {url}: {req.status_code}')

class KafkaClient:
    def __init__(self):
        # servers=os.getenv('KAFKA_SERVERS')
        # topic = os.getenv('KAFKA_TOPIC')
        # key = os.getenv('KAFKA_KEY')
        # self.servers = servers
        # self.producer = KafkaProducer(bootstrap_servers=servers)
        # self.topic = topic
        # self.key = key
        print("DO NOTHING")

    def publish(self, message):
        # self.producer.send(self.topic, message.encode('utf8'))
        print("DO NOTHING")