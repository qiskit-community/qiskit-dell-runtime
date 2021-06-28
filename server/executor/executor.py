from qiskit import Aer

from program import main
from urllib.parse import urljoin
import requests
import os
import sys

from user_messenger_client import RemoteUserMessengerClient

import json
import os
from qiskit.providers.ibmq.runtime.utils import RuntimeDecoder

import logging
import logging.config

logging.config.fileConfig("./logging_config.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

host = os.environ['ORCH_HOST']
job_id = os.environ['JOB_ID']


def main_method():
    params = None
    
    params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'params.json')
    with open(params_path, 'r') as params_file:
        params = params_file.read()
    
    backend = Aer.get_backend('aer_simulator')
    inputs = json.loads(params, cls=RuntimeDecoder)
    user_messenger = RemoteUserMessengerClient()
    
    try:
        main(backend, user_messenger=user_messenger, **inputs)
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main_method()