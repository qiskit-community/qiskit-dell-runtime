from typing import Type, Callable, Optional, Dict
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder

from typing import Union
import tempfile
import shutil
import os
import sys
import logging
import subprocess
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
        
    def _pre_run(self):
        self._temp_dir = tempfile.mkdtemp()
        logger.debug('creating temp directory at ' + self._temp_dir)

        params_path = os.path.join(self._temp_dir, "params.json")
        with open(params_path, "w+") as params_file:
            params_file.write(json.dumps(self._inputs, cls=RuntimeEncoder))
            logger.debug('finished writing to ' + params_path)

        program_path = os.path.join(self._temp_dir, "program.py")
        with open(program_path, "w+") as program_file:
            program_file.write(self._program_data)
            logger.debug('finished writing to ' + program_path)

        executor_path = os.path.join(self._temp_dir, "executor.py")
        executor_content = EXECUTOR_CODE.format(params_path, self._user_messenger.port())
        with open(executor_path, "w+") as executor_file:
            executor_file.write(executor_content)
            logger.debug('finished writing to ' + executor_path)
        
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
from qiskit.providers.ibmq.runtime.utils import RuntimeDecoder

if __name__ == "__main__":
    params = None
    params_path = '{}'	
    with open(params_path, 'r') as params_file:	
        params = params_file.read()
 
    backend = Aer.get_backend('aer_simulator')
    inputs = json.loads(params, cls=RuntimeDecoder)
    user_messenger = LocalUserMessengerClient({})
    main(backend, user_messenger=user_messenger, **inputs)
    print("exit")
"""