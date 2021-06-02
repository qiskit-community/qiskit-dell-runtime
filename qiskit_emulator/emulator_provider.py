import logging
import os

from qiskit.providers.exceptions import QiskitBackendNotFoundError
from qiskit.providers.providerutils import filter_backends
from qiskit.providers import ProviderV1 as Provider

logger = logging.getLogger(__name__)

from . import emulator_backend
from . import emulator_runtime_service
from .remote_runtime_service import RemoteRuntimeService

class EmulatorProvider(Provider):
    name = "emulator_provider"

    def __init__(self):
        super().__init__()
        self._backend_services = BackendService([
            emulator_backend.EmulatorBackend(self)
        ])
        self.local_runtime = emulator_runtime_service.EmulatorRuntimeService(self)
        self.runtime = self.local_runtime
        self.services = {
            'runtime': self.runtime,
        }

    # add authentication later
    def remote(self, host):
        self.runtime = RemoteRuntimeService(self, host)
        self.services['runtime'] = self.runtime

    def local(self):
        self.runtime = self.local_runtime
        self.services['runtime'] = self.local_runtime

    def get_backend(self, name=None, **kwargs):
        backends = self._backend_services(name, **kwargs)
        if len(backends) > 1:
            raise QiskitBackendNotFoundError("More than one backend matches criteria.")
        if not backends:
            raise QiskitBackendNotFoundError("No backend matches criteria.")

        return backends[0]

    def backends(self, name=None, **kwargs):
        return self._backend_services(name=name, **kwargs)

    def services(self):
        return self.services

    def has_service(self, service_name):
        return service_name in self.services

class BackendService:
    def __init__(self, backends):
        self._backends = backends
        for backend in backends:
            setattr(self, backend.name(), backend)

    def __call__(self, name=None, filters=None, **kwargs):
        backends = self._backends
        if name:
            backends = [b for b in self._backends if b.name() == name]
        return filter_backends(backends, filters, **kwargs)
