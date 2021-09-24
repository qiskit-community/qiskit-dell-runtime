from dell_runtime import DellRuntimeProvider
from qiskit import QuantumCircuit

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


def main(
    backend,
    user_messenger,
    circuits,
    **kwargs,
):
    circuits = transpile(
        circuits,
    )

    if not isinstance(circuits, list):
        circuits = [circuits]

    # Compute raw results
    result = backend.run(circuits, **kwargs).result()

    user_messenger.publish(result.to_dict(), final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

# PROGRAM_PREFIX = 'qiskit-test'

def main():
    provider = DellRuntimeProvider()
    program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    program_inputs = {
        'circuits': qc,
    }

    runtime_program = provider.runtime.program(program_id)

    
    job = provider.runtime.run(program_id, options=None, inputs=program_inputs)

    job.result(timeout=120)
    

if __name__ == "__main__":
    main()
