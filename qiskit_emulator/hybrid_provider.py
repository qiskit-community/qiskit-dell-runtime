import logging

logger = logging.getLogger(__name__)
from .emulator_runtime_service import EmulatorRuntimeService
from .remote_runtime_service import RemoteRuntimeService
from .local_sub_provider import LocalSubProviderManager

class DellHybridProvider():

    def __init__(self):
        self.local_runtime = EmulatorRuntimeService(self)
        self.runtime = self.local_runtime
        self.services = {
            'runtime': self.runtime,
        }

    def remote(self, host):
        self.runtime = RemoteRuntimeService(self, host)
        self.services['runtime'] = self.runtime

    def local(self):
        self.runtime = self.local_runtime
        self.services['runtime'] = self.local_runtime

    def services(self):
        return self.services

    def has_service(self, service_name):
        return service_name in self.services