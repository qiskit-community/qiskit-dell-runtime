from qiskit_emulator import EmulatorProvider
import unittest
from urllib.parse import urljoin
import os, requests
import json

ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')

class BackendTest(unittest.TestCase):
    def test_circuit_runner(self):
        provider = EmulatorProvider()
        provider.remote(ACCEPTANCE_URL)
        backends = provider.runtime.backends()
        self.assertGreater(len(backends), 1)