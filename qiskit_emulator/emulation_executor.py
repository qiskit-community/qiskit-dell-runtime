from qiskit.providers.ibmq.runtime import RuntimeProgram
from typing import Union
import tempfile
import shutil
import os

class EmulationExecutor():
    def __init__(self, program: RuntimeProgram, program_data: Union[bytes, str]) -> None:
        self._program = program
        self._program_data = program_data
        self._temp_dir = None
        
    def _pre_run(self):
        self._temp_dir = tempfile.mkdtemp()
        print(self._temp_dir)
        program_path = os.path.join(self._temp_dir, "program.py")
        with open(program_path, "w+") as program_file:
            program_file.write(self._program_data)

        program_file.close()

    def _post_run(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir)

    def temp_dir(self):
        return self._temp_dir

    def run(self):
        try:
            self._pre_run()
        finally:
            self._post_run()

