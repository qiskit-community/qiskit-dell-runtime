from typing import Any, Type
import json
from qiskit.providers.ibmq.runtime import UserMessenger, RuntimeEncoder
from kafka import KafkaProducer
import os

class RemoteUserMessengerClient(UserMessenger):
    def __init__(self):
        self.kafka_client = KafkaClient()

    def publish(
            self,
            message: Any,
            encoder: Type[json.JSONEncoder] = RuntimeEncoder,
            final: bool = False
    ):  
        
        str_msg = json.dumps({"final": final, "message": message}, cls=encoder)
        self.kafka_client.publish(str_msg)

class KafkaClient:
    def __init__(self):
        servers=os.getenv('KAFKA_SERVERS')
        topic = os.getenv('KAFKA_TOPIC')
        key = os.getenv('KAFKA_KEY')
        self.servers = servers
        self.producer = KafkaProducer(bootstrap_servers=servers)
        self.topic = topic
        self.key = key

    def publish(self, message):
        self.producer.send(self.topic, message.encode('utf8'))