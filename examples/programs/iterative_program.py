from dell_runtime import DellRuntimeProvider
from qiskit import QuantumCircuit
import logging
import requests
import time

RUNTIME_PROGRAM = """
# This code is part of qiskit-runtime.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
from qiskit.compiler import transpile, schedule
import time

def main(backend, user_messenger, **kwargs):
    iterations = kwargs.pop("iterations", 5)
    for it in range(iterations):
        user_messenger.publish({"iteration": it })
        time.sleep(5)

    user_messenger.publish("All done!", final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

PROGRAM_PREFIX = 'qiskit-test'
REMOTE_RUNTIME = 'http://localhost:8080'
def main():
    print("Starting...")
    logging.basicConfig(level=logging.DEBUG)

    provider = DellRuntimeProvider()
    # provider.remote(REMOTE_RUNTIME)
    program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
    print(f"PROGRAM ID: {program_id}")


    program_inputs = {
        'iterations': 3,
    }

    
    job = provider.runtime.run(program_id, options=None, inputs=program_inputs)
    time.sleep(2)
    print(job.get_unread_messages())
    results = job.result(timeout=25)
    print(results)
if __name__ == "__main__":
    main()