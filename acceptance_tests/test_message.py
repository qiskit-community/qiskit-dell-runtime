import unittest
from urllib.parse import urljoin
import os, requests
import json

ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')

class MessageTest(unittest.TestCase):
    def test_save_message(self):
        job_id = "test_job"
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/delete_message')
        req = requests.get(url)
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/message')
        req = requests.post(url, json='testing message')
        self.assertEqual(200, req.status_code)


    #TODO: Update re: SSO changes.
    # To get results, we need:
    # A message in the DB, which is attached to a job
    # This means the job needs to be created and 
    # associated with a user.
    # We aren't doing that rn, so no one owns "test_job2"
    # And therefore literally no one can get the results
    # of that job

    # I think to fix this test is essentially to write a 
    # test_get_results which already exists in acceptance. 
    # I don't know if we need this file anymore.
    # def test_get_message(self):
    #     job_id = "test_job2"
    #     url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/delete_message')
    #     req = requests.get(url)
    #     url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/message')
    #     req = requests.post(url, data='testing message two')
    #     self.assertEqual(200, req.status_code)
    #     url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/results')
    #     res = requests.get(url)

    #     msg = json.loads(res.text)

    #     self.assertEqual(200, res.status_code)
    #     self.assertEqual('testing message two', msg['messages'][0]['data'])
