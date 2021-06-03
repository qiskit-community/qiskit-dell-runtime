from qiskit_emulator import EmulatorProvider
from qiskit import QuantumCircuit
import logging

RUNTIME_PROGRAM = """
import random

from qiskit import transpile
from qiskit.circuit.random import random_circuit

def prepare_circuits(backend):
    circuit = random_circuit(num_qubits=5, depth=4, measure=True,
                            seed=random.randint(0, 1000))
    return transpile(circuit, backend)

def main(backend, user_messenger, **kwargs):
    # iterations = kwargs['iterations']
    iterations = 3
    # interim_results = kwargs.pop('interim_results', {})
    # final_result = kwargs.pop("final_result", {})
    for it in range(iterations):
        qc = prepare_circuits(backend)
        # user_messenger.publish({"iteration": it, "interim_results": interim_results})
        backend.run(qc).result()

    # user_messenger.publish(final_result, final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

PROGRAM_PREFIX = 'qiskit-test'

def main():
    print("Starting...")
    logging.basicConfig(level=logging.DEBUG)

    provider = EmulatorProvider()
    provider.remote('http://100.80.243.207')
    program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA, description="basic execution 2")
    print(f"PROGRAM ID: {program_id}")

if __name__ == "__main__":
    main()