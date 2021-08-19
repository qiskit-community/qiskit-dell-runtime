from qiskit.opflow import Z, I
from qiskit.circuit.library import EfficientSU2
import numpy as np
from qiskit.algorithms.optimizers import SPSA
from qiskit_emulator import DellHybridProvider
import os
from time import sleep
from datetime import datetime, timedelta

num_qubits = 4
hamiltonian = (Z ^ Z) ^ (I ^ (num_qubits - 2))
target_energy = -1


# the rotation gates are chosen randomly, so we set a seed for reproducibility
ansatz = EfficientSU2(num_qubits, reps=1, entanglement='linear', insert_barriers=True)
# ansatz.draw('mpl', style='iqx')

optimizer = SPSA(maxiter=50)

np.random.seed(10)  # seed for reproducibility
initial_point = np.random.random(ansatz.num_parameters)

intermediate_info = {
    'nfev': [],
    'parameters': [],
    'energy': [],
    'stddev': []
}

timestamps = []

def raw_callback(*args):
    # print(args)
    (nfev, parameters, energy, stddev) = args[0]
    intermediate_info['nfev'].append(nfev)
    intermediate_info['parameters'].append(parameters)
    intermediate_info['energy'].append(energy)
    intermediate_info['stddev'].append(stddev)
    # timestamps.append(datetime.now())
    print(str(datetime.now()))
    print(intermediate_info)

vqe_inputs = {
    'ansatz': ansatz,
    'operator': hamiltonian,
    'optimizer': {'name': 'SPSA', 'maxiter': 15},  # let's only do a few iterations!
    'initial_point': initial_point,
    'measurement_error_mitigation': True,
    'shots': 1024,
}

provider = DellHybridProvider()
provider.remote(os.getenv("SERVER_URL"))

program_id = provider.runtime.upload_program("vqe.py")

job = provider.runtime.run(
    program_id=program_id,
    inputs=vqe_inputs,
    options=None,
    callback=raw_callback
)

# timestamps.append(datetime.now())

print('Job ID:', job.job_id)

result = job.result()
while not result:
    print('no result yet.')
    sleep(0.5)
    result = job.result()

# timestamps.append(datetime.now())

# deltas = []
# for i in range(1, len(timestamps)):
#     deltas.append(timestamps[i] - timestamps[i-1])

print(f"Intermediate Results: {intermediate_info}")
print(f'Reached {result["optimal_value"]} after {result["optimizer_evals"]} evaluations.')
print('Available keys:', list(result.keys()))
