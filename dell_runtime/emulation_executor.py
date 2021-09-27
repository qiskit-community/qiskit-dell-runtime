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
from dell_runtime import LocalUserMessengerClient
from dell_runtime import BackendProvider
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

    inputs = json.loads(params, cls=RuntimeDecoder)
    backend = None
    provider = BackendProvider()
    if 'backend_name' in inputs:
        provider = BackendProvider()
        print(inputs)
        backend_name = inputs['backend_name']
        print("using backend: " + backend_name)
        if 'backend_token' in inputs:
            print('backend with token!')
            backend = provider.get_backend(name = backend_name, backend_token=inputs["backend_token"])
        else:
            backend = provider.get_backend(name = backend_name)
    else:
        print("using default backend: " + 'aer_simulator')
        backend = provider.get_backend('aer_simulator')

    user_messenger = LocalUserMessengerClient({})
    try:
        main(backend, user_messenger=user_messenger, **inputs)
        
    except Exception as e:
        print(e)
        sys.exit(1)
    print("exit")
  
"""