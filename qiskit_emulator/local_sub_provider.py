from qiskit import Aer
from qiskit_ionq import IonQProvider
from qiskit.providers.exceptions import QiskitBackendNotFoundError
# from qiskit import IBMQ

from .emulator_backend import EmulatorBackend

class LocalSubProviderManager():
    def __init__(self, provider):
        # self.sub_providers = [Aer, IonQProvider(), IBMQ.get_provider()]
        # self.sub_providers = [Aer, IonQProvider()]
        self._provider = provider
        self._init_backends()
            
    def _init_backends(self):
        self._backends = [Aer.get_backend('aer_simulator')]
        self._backends.append(EmulatorBackend(self._provider))
        self._backends += IonQProvider().backends()

        # for sub_provider in self.sub_providers:
            # self._backends += sub_provider.backends()
        
        self._backends_by_name = {}
        for backend in self._backends:
            self._backends_by_name[backend.name()] = backend


    def backends(self):
        return self._backends

    def get_backend(self, name=None, **kwargs):
        if name not in self._backends_by_name:
            raise QiskitBackendNotFoundError("No backend matches criteria.")
        else:
            if "ionq" in name:
                if 'backend_token' in kwargs:
                    backends = IonQProvider(token=kwargs['backend_token']).backends()
                    backend_dict = {}
                    for backend in backends:
                        backend_dict[backend.name()] = backend
                    return backend_dict[name]
                else:
                    raise Exception('token required with ionq')
            return self._backends_by_name[name]



    
