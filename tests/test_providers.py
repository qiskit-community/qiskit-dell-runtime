import unittest
from dell_runtime import DellRuntimeProvider, BackendProvider

class ProviderTest(unittest.TestCase):
    def test_new_provider(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)
        provider = BackendProvider()
        self.assertIsNotNone(provider)

    def test_backends(self):
        provider = BackendProvider()
        self.assertIsNotNone(provider)

        self.assertGreater(len(provider.backends()), 1)

    def test_runtime_supported(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)

        self.assertTrue(provider.has_service('runtime'))
        self.assertFalse(provider.has_service('weird_service'))

    def test_has_runtime_attribute(self):
        provider = DellRuntimeProvider()
        self.assertIsNotNone(provider)

        self.assertIsNotNone(provider.runtime)

