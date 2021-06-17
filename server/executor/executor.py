from qiskit import Aer

from program import main
from user_messenger_client import RemoteUserMessengerClient

import json
import os
from qiskit.providers.ibmq.runtime.utils import RuntimeDecoder

def main_method():
    params = None
    
    params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'params.json')
    with open(params_path, 'r') as params_file:
        params = params_file.read()
    
    backend = Aer.get_backend('aer_simulator')
    inputs = json.loads(params, cls=RuntimeDecoder)
    user_messenger = RemoteUserMessengerClient()

    # Wrap in try/except to determine whether or not job fails
    # Call back to orch to tell whether job succeed/fail

    main(backend, user_messenger=user_messenger, **inputs)
    print("exit")

if __name__ == "__main__":
    main_method()