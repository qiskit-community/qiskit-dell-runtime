import logging
import os

from qiskit.providers import ProviderV1 as Provider

logger = logging.getLogger(__name__)

from .local_sub_provider import LocalSubProviderManager

class BackendProvider(Provider):

    def __init__(self):
        super().__init__()
        self.sub_provider_manager = LocalSubProviderManager(self)
        self.services = {
        }

    def get_backend(self, name=None, **kwargs):
        return self.sub_provider_manager.get_backend(name=name, **kwargs)
        
    def backends(self, name=None, **kwargs):
        return self.sub_provider_manager.backends()

