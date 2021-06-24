from typing import Type, Callable, Optional, Dict, Tuple
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
import multiprocessing 
import ctypes
from time import sleep
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CREATING = "Creating"
RUNNING = "Running"
COMPLETED = "Completed"
FAILED = "Failed"
CANCELED = "Canceled"

STATUS_VALUES = [CREATING, RUNNING, COMPLETED, FAILED, CANCELED]

STRING = "STRING"
DIR = "DIR"

class EmulationExecutor():

    def __init__(self, program: RuntimeProgram, program_data: Tuple[Union[bytes, str], str],
            options: Dict = {},
            inputs: Dict = {},
            callback: Optional[Callable] = None, 
            result_decoder: Optional[Type[ResultDecoder]] = None) -> None:
        self._program = program
        self._program_data = program_data
        
        self._options = options
        self._inputs = inputs
        
        self._temp_dir = None
        self._local_port = 0

        self._statusvalue = multiprocessing.Value(ctypes.c_int)
        self._statusvalue.value = STATUS_VALUES.index(CREATING)
        self._xprocess = multiprocessing.Process(target=self._execute,args =(self._statusvalue,))

    def __del__(self):
        if self._xprocess.is_alive():
            try:
                self._xprocess().terminate()
                while self._xprocess.is_alive():
                    pass
            except Exception as e:
                logger.debug("terminating process with : ")

    def _pre_run(self):
        self._temp_dir = tempfile.mkdtemp()
        logger.debug('creating temp directory at ' + self._temp_dir)

        if self._program_data[1] == STRING:
            program_path = os.path.join(self._temp_dir, "program.py")
            with open(program_path, "w+") as program_file:
                program_file.write(self._program_data[0])
                logger.debug('finished writing to ' + program_path)
        elif self._program_data[1] == DIR:
            shutil.unpack_archive(self._program_data[0], extract_dir=self._temp_dir, format="zip")
            logger.debug("finished extracting archive")

        params_path = os.path.join(self._temp_dir, "params.json")
        with open(params_path, "w+") as params_file:
            params_file.write(json.dumps(self._inputs, cls=RuntimeEncoder))
            logger.debug('finished writing to ' + params_path)

        executor_path = os.path.join(self._temp_dir, "executor.py")
        executor_content = EXECUTOR_CODE.format(params_path, self._local_port)
        with open(executor_path, "w+") as executor_file:
            executor_file.write(executor_content)
            logger.debug('finished writing to ' + executor_path)

        

    def _post_run(self):
        try:
            if self._temp_dir is not None:
                shutil.rmtree(self._temp_dir)
        except:
            logger.debug("Its gone")
        

    def temp_dir(self):
        return self._temp_dir

    def _execute(self, statusvalue):
        statusvalue.value = STATUS_VALUES.index(RUNNING)
        try:
            executor_path = os.path.join(self._temp_dir, "executor.py")
            cmd = [sys.executable, executor_path]
            logger.debug(f"starting {cmd}")
            exec_result = subprocess.run(cmd, capture_output=True, text=True)
            logger.debug(f"finished executing {cmd}")
            logger.debug(f"stdout: {exec_result.stdout}")
            logger.debug(f"stderr: {exec_result.stderr}")
            exec_result.check_returncode()
            statusvalue.value = STATUS_VALUES.index(COMPLETED)
            logger.debug(f"status: sent COMPLETED")
            self._post_run()
            sys.exit(0)
        except Exception as e:
            statusvalue.value = STATUS_VALUES.index(FAILED)
            self._post_run()
            logger.debug(f"status: sent FAILED")
            sys.exit(1)

            
    def run(self):
        self._pre_run()
        self._xprocess.start()

    def get_status(self):
        return STATUS_VALUES[self._statusvalue.value]

    def cancel(self):
        self._xprocess.kill()
        
        while self._xprocess.is_alive():
            sleep(1)     
        self._statusvalue.value = STATUS_VALUES.index(CANCELED)
        self._post_run()


EXECUTOR_CODE = """
from qiskit import Aer
from qiskit_emulator import LocalUserMessengerClient
from program import main
import sys
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
    try:
        main(backend, user_messenger=user_messenger, **inputs)
        
    except Exception as e:
        print(e)
        sys.exit(1)
    print("exit")
  
"""