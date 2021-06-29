import requests
import os
from urllib.parse import urljoin
import sys
import subprocess
import shutil
import base64
import json

import logging
import logging.config

logging.config.fileConfig("./logging_config.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# res = (req.status_code, req.reason, req.text)
host = os.environ['ORCH_HOST']
program_id = os.environ['PROGRAM_ID']
inputs_str = os.environ['INPUTS_STR']
job_id = os.environ['JOB_ID']
RUNNING = "Running"
COMPLETED = "Completed"
FAILED = "Failed"

qre_dir = "/var/qiskit-runtime"
# qre_dir = "/root/workspace/qre-runtime-test"
executor_path = os.path.join(qre_dir, 'executor.py')
program_path = os.path.join(qre_dir, 'program.py')
params_path = os.path.join(qre_dir, 'params.json')

STRING = "STRING"
DIR = "DIR"

def write_program_params_file():
    with open(params_path, "w+") as params_file:
        params_file.write(inputs_str)
        logger.debug('finished writing to ' + params_path)

def download_program_from_orchestrator():
    url = urljoin(host, f'/program/{program_id}/data')
    req = requests.get(url)
    if req.status_code != 200:
        raise (f'Error GET {url}: {req.status_code}')

    logger.debug('received program data ' + program_path)
    
    
    if "application/zip" in req.headers.get('content-type'):
        logger.debug('received directory')
        
        logger.debug("to bytes")
        tmpzip = os.path.join(qre_dir, "tmpzip.zip")
        with open(tmpzip, "wb+") as temp:
            temp.write(req.content)
        logger.debug(req.content)
        logger.debug(f'wrote bytes to zip {tmpzip}')
        shutil.unpack_archive(tmpzip, extract_dir=qre_dir, format="zip")
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
        raise (f'Error POST {url}: {req.status_code}')

    

def main():
    print("RUNNING!")
    try:
        write_program_params_file()
        download_program_from_orchestrator()
        update_status(RUNNING)
        
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