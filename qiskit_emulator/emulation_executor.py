from typing import Type, Callable, Optional, Dict
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder

from typing import Union
import tempfile
import shutil
import os
import sys
import logging
import subprocess
import json

logger = logging.getLogger(__name__)

from .local_user_messenger import LocalUserMessenger

class EmulationExecutor():

    def __init__(self, program: RuntimeProgram, program_data: Union[bytes, str],
            options: Dict = {},
            inputs: Dict = {}, 
            callback: Optional[Callable] = None, 
            result_decoder: Optional[Type[ResultDecoder]] = None) -> None:
        self._program = program
        self._program_data = program_data
        
        self._options = options
        self._inputs = inputs
        self._user_messenger = LocalUserMessenger()
        
        self._temp_dir = None

    def _save_params(self):
        params = json.dumps({
            "options": self._options,
            "inputs": self._inputs,
            "messenger": {
                "port": self._user_messenger.port()
            }
        })
        params_path = os.path.join(self._temp_dir, "params.json")
        with open(params_path, "w+") as params_file:
            params_file.write(params)
            logger.debug('finished writing to ' + params_path)
        
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

        self._save_params()
        
    def _post_run(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir)
            self._user_messenger.close()

    def temp_dir(self):
        return self._temp_dir

    def _execute(self):
        self._user_messenger.listen()

        executor_path = os.path.join(self._temp_dir, "executor.py")
        cmd = [sys.executable, executor_path]
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
from qiskit_emulator import LocalUserMessengerClient
from program import main
import json
import os

if __name__ == "__main__":
    params = None
    params_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "params.json")
    with open(params_path, 'r') as params_file:
        params = json.load(params_file)

    backend = Aer.get_backend('aer_simulator')
    user_messenger = LocalUserMessengerClient(params['messenger']['port'])

    main(backend, user_messenger=user_messenger, **{
        "iterations": 2
    })
    print("exit")
"""