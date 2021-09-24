from dell_runtime import DellRuntimeProvider
from qiskit import QuantumCircuit
import os

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

# This is a simplified version of the circuit-runner program.

from qiskit.compiler import transpile, schedule


def main(
    backend,
    user_messenger,
    circuits,
    initial_layout=None,
    seed_transpiler=None,
    optimization_level=None,
    transpiler_options=None,
    scheduling_method=None,
    schedule_circuit=False,
    inst_map=None,
    meas_map=None,
    measurement_error_mitigation=False,
    **kwargs,
):

    # transpiling the circuits using given transpile options
    transpiler_options = transpiler_options or {}
    circuits = transpile(
        circuits,
        initial_layout=initial_layout,
        seed_transpiler=seed_transpiler,
        optimization_level=optimization_level,
        backend=backend,
        **transpiler_options,
    )

    if schedule_circuit:
        circuits = schedule(
            circuits=circuits,
            backend=backend,
            inst_map=inst_map,
            meas_map=meas_map,
            method=scheduling_method,
        )

    if not isinstance(circuits, list):
        circuits = [circuits]

    # Compute raw results
    result = backend.run(circuits, **kwargs).result()

    if measurement_error_mitigation:
        # Performs measurement error mitigation.
        pass

    user_messenger.publish(result.to_dict(), final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

PROGRAM_PREFIX = 'qiskit-test'
def main():
    provider = DellRuntimeProvider()
    program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
    N = 6
    qc = QuantumCircuit(N)

    qc.x(range(0, N))
    qc.h(range(0, N))

    for kk in range(N//2,0,-1):
        qc.ch(kk, kk-1)
    for kk in range(N//2, N-1):
        qc.ch(kk, kk+1)
    qc.measure_all()

    program_inputs = {
        'circuits': qc,
        'shots': 2048,
        'optimization_level': 0,
        'initial_layout': [0,1,4,7,10,12],
        'measurement_error_mitigation': False
    }

    runtime_program = provider.runtime.program(program_id)

    
    job = provider.runtime.run(program_id, options=None, inputs=program_inputs)

    res = job.result(timeout=10)

    print(f"res: {res}")

if __name__ == "__main__":
    main()
