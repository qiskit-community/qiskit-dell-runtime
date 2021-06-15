import requests
import os
from urllib.parse import urljoin
import sys
import subprocess

import logging
import logging.config

logging.config.fileConfig("./logging_config.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# res = (req.status_code, req.reason, req.text)
host = os.environ['ORCH_HOST']
program_id = os.environ['PROGRAM_ID']
inputs_str = os.environ['INPUTS_STR']

qre_dir = "/var/qiskit-runtime"
# qre_dir = "/root/workspace/qre-runtime-test"
executor_path = os.path.join(qre_dir, 'executor.py')
program_path = os.path.join(qre_dir, 'program.py')
params_path = os.path.join(qre_dir, 'params.json')

def write_program_params_file():
    with open(params_path, "w+") as params_file:
        params_file.write(inputs_str)
        logger.debug('finished writing to ' + params_path)

def download_program_from_orchestrator():
    url = urljoin(host, f'/program/{program_id}/data')
    req = requests.get(url)
    if req.status_code != 200:
        raise (f'Error GET {url}: {req.status_code}')
    
    with open(program_path, "w+") as program_file:
        program_file.write(req.text)
        logger.debug('finished writing to ' + program_path)

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
    except Exception as e:
        logger.error(e)
    print("EXIT")

if __name__ == "__main__":
    main()