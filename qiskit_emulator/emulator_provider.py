import logging
import os


from qiskit.providers.providerutils import filter_backends
from qiskit.providers import ProviderV1 as Provider

logger = logging.getLogger(__name__)


from . import emulator_runtime_service
from .remote_runtime_service import RemoteRuntimeService
from .local_sub_provider import LocalSubProviderManager
from .remote_sub_provider import RemoteSubProviderManager


class EmulatorProvider(Provider):
    name = "emulator_provider"

    def __init__(self):
        super().__init__()
        # self._backend_services = BackendService([
        #     emulator_backend.EmulatorBackend(self)
        # ])
        self.sub_provider_manager = LocalSubProviderManager(self)
        self.local_runtime = emulator_runtime_service.EmulatorRuntimeService(self)
        self.runtime = self.local_runtime
        self.services = {
            'runtime': self.runtime,
        }

    # add authentication later
    def remote(self, host):
        self.runtime = RemoteRuntimeService(self, host)
        self.services['runtime'] = self.runtime
        self.sub_provider_manager = RemoteSubProviderManager()

    def local(self):
        self.runtime = self.local_runtime
        self.sub_provider_manager = LocalSubProviderManager(self)
        self.services['runtime'] = self.local_runtime

    def get_backend(self, name=None, **kwargs):
        return self.sub_provider_manager.get_backend(name=name, **kwargs)
        
    def backends(self, name=None, **kwargs):
        return self.sub_provider_manager.backends()
        # return self._backend_services(name=name, **kwargs)

    def services(self):
        return self.services

    def has_service(self, service_name):
        return service_name in self.services

# class BackendService:
#     def __init__(self, backends):
#         self._backends = backends
#         for backend in backends:
#             setattr(self, backend.name(), backend)

#     def __call__(self, name=None, filters=None, **kwargs):
#         backends = self._backends
#         if name:
#             backends = [b for b in self._backends if b.name() == name]
#         return filter_backends(backends, filters, **kwargs)
