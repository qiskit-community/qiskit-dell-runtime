from qiskit import Aer

from program import main
from urllib.parse import urljoin
import requests
import os

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
COMPLETED = "Completed"
FAILED = "Failed"


def update_status(status):
    logger.debug(f'Updating status to {status}')
    url = urljoin(host, f'/job/{job_id}/status')
    req = requests.post(url, json=status)
    if req.status_code != 200:
        raise (f'Error POST {url}: {req.status_code}')

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
        update_status(COMPLETED)
    except Exception as e:
        print(e)
        update_status(FAILED)

    print("exit")

if __name__ == "__main__":
    main_method()