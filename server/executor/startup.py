# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# Copyright 2021 Dell (www.dell.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests
import os
from urllib.parse import urljoin
import sys
import subprocess
import shutil
import logging
import logging.config

logging.config.fileConfig("./logging_config.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# res = (req.status_code, req.reason, req.text)
data_token = os.environ['DATA_TOKEN']
host = os.environ['ORCH_HOST']
program_id = os.environ['PROGRAM_ID']
inputs_str = os.environ['INPUTS_STR']
job_id = os.environ['JOB_ID']
COMPLETED = "Completed"
FAILED = "Failed"

qdr_dir = "/var/qiskit-runtime"
# qdr_dir = "/root/workspace/qdr-runtime-test"
executor_path = os.path.join(qdr_dir, 'executor.py')
program_path = os.path.join(qdr_dir, 'program.py')
params_path = os.path.join(qdr_dir, 'params.json')

STRING = "STRING"
DIR = "DIR"

def write_program_params_file():
    with open(params_path, "w+") as params_file:
        params_file.write(inputs_str)
        logger.debug('finished writing to ' + params_path)

def download_program_from_orchestrator():
    url = urljoin(host, f'/program/{program_id}/data')
    req = requests.get(url, data={'job_id': job_id, 'token': data_token})
    if req.status_code != 200:
        raise Exception(f'Error GET {url}: {req.status_code}')

    logger.debug('received program data ' + program_path)
    
    
    if "application/zip" in req.headers.get('content-type'):
        logger.debug('received directory')
        
        logger.debug("to bytes")
        tmpzip = os.path.join(qdr_dir, "tmpzip.zip")
        with open(tmpzip, "wb+") as temp:
            temp.write(req.content)
        logger.debug(req.content)
        logger.debug(f'wrote bytes to zip {tmpzip}')
        shutil.unpack_archive(tmpzip, extract_dir=qdr_dir, format="zip")
        logger.debug('unpacked archive')
        os.remove(tmpzip)
        logger.debug("finished unpacking directory")
    elif "text/plain" in req.headers.get('content-type'):
        with open(program_path, "wb+") as program_file:
            program_file.write(req.content)
            logger.debug('finished writing to ' + program_path)
    else:
        logger.debug(f'content type received: {req.headers.get("content-type")}')

def update_status(status):
    logger.debug(f'Updating status to {status}')
    url = urljoin(host, f'/job/{job_id}/status')
    req = requests.post(url, json=status)
    if req.status_code != 200:
        raise Exception(f'Error POST {url}: {req.status_code}')

    

def main():
    print("RUNNING!")
    try:
        write_program_params_file()
        download_program_from_orchestrator()
        
        cmd = [sys.executable, executor_path]
        exec_result = subprocess.run(cmd, capture_output=True, text=True)
        logger.debug(f"finished executing {cmd}")
        logger.debug(f"stdout: {exec_result.stdout}")
        logger.debug(f"stderr: {exec_result.stderr}")
        exec_result.check_returncode()
        update_status(COMPLETED)
    except Exception as e:
        logger.error(e)
        update_status(FAILED)
    print("EXIT")

if __name__ == "__main__":
    main()