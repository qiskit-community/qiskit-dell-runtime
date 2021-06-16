import unittest
from urllib.parse import urljoin
import os, requests

ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')

class MessageTest(unittest.TestCase):
    def test_save_message(self):
        job_id = "test_job"
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/delete_message')
        req = requests.get(url)
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/message')
        req = requests.post(url, json='testing message')
        self.assertEqual(200, req.status_code)

    def test_get_message(self):
        job_id = "test_job2"
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/delete_message')
        req = requests.get(url)
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/message')
        req = requests.post(url, json='testing message two')
        self.assertEqual(200, req.status_code)
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/results')
        res = requests.get(url)
        self.assertEqual(200, res.status_code)
        self.assertEqual("testing message two", res.text)
