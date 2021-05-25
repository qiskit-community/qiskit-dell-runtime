from qiskit.providers import BackendV1 as Backend
from qiskit.providers.models import BackendConfiguration
from qiskit.providers.models.backendstatus import BackendStatus
from qiskit.providers import Options

# from . import emulator_job

class EmulatorBackend(Backend):
    def __init__(self, provider):
        default_basic_gates = sorted([
            'u1', 'u2', 'u3', 'u', 'p', 'r', 'rx', 'ry', 'rz', 'id', 'x',
            'y', 'z', 'h', 's', 'sdg', 'sx', 't', 'tdg', 'swap', 'cx',
            'cy', 'cz', 'csx', 'cp', 'cu1', 'cu2', 'cu3', 'rxx', 'ryy',
            'rzz', 'rzx', 'ccx', 'cswap', 'mcx', 'mcy', 'mcz', 'mcsx',
            'mcphase', 'mcu1', 'mcu2', 'mcu3', 'mcrx', 'mcry', 'mcrz',
            'mcr', 'mcswap', 'unitary', 'diagonal', 'multiplexer',
            'initialize', 'delay', 'pauli', 'mcx_gray'
        ])
        default_config = { #https://qiskit.org/documentation/stubs/qiskit.providers.models.BackendConfiguration.html#qiskit.providers.models.BackendConfiguration
            'backend_name': 'emulator',
            'backend_version': "0.1.0",
            'n_qubits': 29,
            'url': 'https://github.com/Qiskit/qiskit-aer',
            'simulator': True,
            'local': True,
            'conditional': True,
            'open_pulse': False,
            'memory': True,
            'max_shots': int(1e6),
            'description': 'A emulator backend',
            'coupling_map': None,
            'basis_gates': default_basic_gates,
            'gates': []
        }
    
        super().__init__(configuration=BackendConfiguration.from_dict(default_config), provider=provider)

    @classmethod
    def _default_options(cls):
        return Options(shots=1, sampler_seed=None)

    def run(self, circuits, **kwargs):
        # job = emulator_job.EmulatorJob(self, None)
        # job.submit()
        # return job
        return None

    def status(self):
        # backend_name (str) – The backend’s name
        # backend_version (str) – The backend’s version of the form X.Y.Z
        # operational (bool) – True if the backend is operational
        # pending_jobs (int) – The number of pending jobs on the backend
        # status_msg (str) – The status msg for the backend
        return BackendStatus(
            backend_name=self.name(),
            backend_version="1",
            operational=True,
            pending_jobs=0,
            status_msg="",
        )