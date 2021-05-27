from qiskit.providers.ibmq.runtime import RuntimeProgram
from typing import Union
import tempfile
import shutil
import os
import logging
import subprocess

logger = logging.getLogger(__name__)

class EmulationExecutor():


    def __init__(self, program: RuntimeProgram, program_data: Union[bytes, str]) -> None:
        self._program = program
        self._program_data = program_data
        self._temp_dir = None
        
    def _pre_run(self):
        self._temp_dir = tempfile.mkdtemp()
        logger.debug('creating temp directory at ' + self._temp_dir)

        program_path = os.path.join(self._temp_dir, "program.py")
        with open(program_path, "w+") as program_file:
            program_file.write(self._program_data)
            logger.debug('finished writing to ' + program_path)

        executor_path = os.path.join(self._temp_dir, "executor.py")
        with open(executor_path, "w+") as executor_file:
            executor_file.write(EXECUTOR_CODE)
            logger.debug('finished writing to ' + executor_path)
        
    def _post_run(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir)

    def temp_dir(self):
        return self._temp_dir

    def _execute(self):
        executor_path = os.path.join(self._temp_dir, "executor.py")
        cmd = ["python", executor_path]
        logger.debug(f"starting {cmd}")
        exec_result = subprocess.run(cmd, capture_output=True, text=True)
        logger.debug(f"finished executing {cmd}")
        logger.debug(f"stdout: {exec_result.stdout}")
        logger.debug(f"stderr: {exec_result.stderr}")
        exec_result.check_returncode()

    def run(self):
        try:
            self._pre_run()
            self._execute()
        finally:
            self._post_run()

EXECUTOR_CODE = """
from qiskit import Aer
from program import main

if __name__ == "__main__":
    backend = Aer.get_backend('aer_simulator')

    main(backend, user_messenger=None, **{
        "iterations": 2
    })
    print("exit")
"""