import unittest
from urllib.parse import urljoin
import os, requests
import json

SERVER_URL = os.getenv('SERVER_URL')

class MessageTest(unittest.TestCase):
    def test_save_message_unregistered(self):
        job_id = "test_job"
        url = urljoin(SERVER_URL, f'/job/{job_id}/message')
        req = requests.post(url, json='testing message')
        self.assertNotEqual(200, req.status_code)

