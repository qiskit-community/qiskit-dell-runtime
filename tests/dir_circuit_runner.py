from dell_runtime import DellRuntimeProvider
from qiskit import QuantumCircuit
import os

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

# PROGRAM_PREFIX = 'qiskit-test'

def main():
    provider = DellRuntimeProvider()
    here = os.path.dirname(os.path.realpath(__file__))
    program_id = provider.runtime.upload_program(here + "/dirtest", metadata=RUNTIME_PROGRAM_METADATA)
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    program_inputs = {
        'circuits': qc,
    }

    job = provider.runtime.run(program_id, options=None, inputs=program_inputs)

    job.result(timeout=120)
    

if __name__ == "__main__":
    main()
