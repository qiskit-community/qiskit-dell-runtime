import requests
import os
from urllib.parse import urljoin
import sys
import subprocess

import logging
logger = logging.getLogger(__name__)

# res = (req.status_code, req.reason, req.text)
def main():
    host = os.environ['ORCH_HOST']
    program_id = os.environ['PROGRAM_ID']
    url = urljoin(host, f'/program/{program_id}/data')
    req = requests.get(url)
    if req.status_code != 200:
        logger.error(f'Error GET {url}: {req.status_code}')
    else:
        program_path = os.path.join('/var/qiskit-runtime', 'program.py')
        print(req.text)
        with open(program_path, "w+") as program_file:
            program_file.write(req.text)
            logger.debug('finished writing to ' + program_path)
        executor_path = os.path.join('/var/qiskit-runtime', 'executor.py')
        cmd = [sys.executable, executor_path]
        exec_result = subprocess.run(cmd, capture_output=True, text=True)
        logger.debug(f"finished executing {cmd}")
        logger.debug(f"stdout: {exec_result.stdout}")
        logger.debug(f"stderr: {exec_result.stderr}")
        exec_result.check_returncode()

if __name__ == "__main__":
    main()