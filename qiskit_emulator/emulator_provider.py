import logging
import os

from qiskit.providers.exceptions import QiskitBackendNotFoundError
from qiskit.providers.providerutils import filter_backends

logger = logging.getLogger(__name__)

from . import emulator_backend

class EmulatorProvider:
    name = "emulator_provider"

    def __init__(self):
        self.backends = BackendService([
            emulator_backend.EmulatorBackend(self)
        ])

    def get_backend(self, name=None, **kwargs):
        backends = self.backends(name, **kwargs)
        if len(backends) > 1:
            raise QiskitBackendNotFoundError("More than one backend matches criteria.")
        if not backends:
            raise QiskitBackendNotFoundError("No backend matches criteria.")

        return backends[0]

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
