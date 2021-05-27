import unittest
from qiskit_emulator import EmulatorProvider
import os

# from ..qiskit_emulator.emulation_executor import EmulationExecutor
from qiskit_emulator import EmulationExecutor

class EmulationExecutorTest(unittest.TestCase):
    def test_pre_run(self):
        try:
            executor = EmulationExecutor(program=None, program_data="abcd")
            self.assertIsNotNone(executor)

            executor._pre_run()
            self.assertTrue(os.path.isdir(executor.temp_dir()))

            program_path = os.path.join(executor.temp_dir(), "program.py")
            self.assertTrue(os.path.isfile(program_path))
        finally:
            executor._post_run()
            self.assertFalse(os.path.isdir(executor.temp_dir()))



        

        