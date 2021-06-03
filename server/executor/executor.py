from qiskit import Aer

from program import main
from user_messenger_client import RemoteUserMessengerClient

import json
import os
from qiskit.providers.ibmq.runtime.utils import RuntimeDecoder


def main_method():
    # params = None
    # params_path = '{}'	
    # with open(params_path, 'r') as params_file:	
    #     params = params_file.read()
 
    backend = Aer.get_backend('aer_simulator')
    # inputs = json.loads(params, cls=RuntimeDecoder)
    inputs = {}
    user_messenger = RemoteUserMessengerClient()
    main(backend, user_messenger=user_messenger, **inputs)
    print("exit")

if __name__ == "__main__":
    main_method()