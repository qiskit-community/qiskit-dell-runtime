import unittest
from qiskit_emulator import EmulatorProvider
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.runtime_program import ProgramParameter, ProgramResult
RUNTIME_PROGRAM = """
import random

from qiskit import transpile
from qiskit.circuit.random import random_circuit

def prepare_circuits(backend):
    circuit = random_circuit(num_qubits=5, depth=4, measure=True,
                            seed=random.randint(0, 1000))
    return transpile(circuit, backend)

def main(backend, user_messenger, **kwargs):
    iterations = kwargs['iterations']
    interim_results = kwargs.pop('interim_results', {})
    final_result = kwargs.pop("final_result", {})
    for it in range(iterations):
        qc = prepare_circuits(backend)
        # user_messenger.publish({"iteration": it, "interim_results": interim_results})
        backend.run(qc).result()

    # user_messenger.publish(final_result, final=True)
"""

RUNTIME_PROGRAM_METADATA = {
    "name": "qiskit-test",
    "description": "Test program.",
    "max_execution_time": 300,
    "version": "0.1",
    "backend_requirements": {"min_num_qubits":  5},
    "parameters": [
        {"name": "param1", "description": "Some parameter.",
            "type": "integer", "required": True}
    ],
    "return_values": [
        {"name": "ret_val", "description": "Some return value.", "type": "string"}
    ],
    "interim_results": [
        {"name": "int_res", "description": "Some interim result", "type": "string"},
    ]
}

PROGRAM_PREFIX = 'qiskit-test'

class EmulatorRuntimeServiceTest(unittest.TestCase):
    def test_upload_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        self.assertEqual(0, len(provider.runtime.programs()))
        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

    def test_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

        runtime_program = provider.runtime.program('fake_id')
        self.assertIsNone(runtime_program)

        runtime_program = provider.runtime.program(program_id)
        self.assertIsNotNone(runtime_program)

    def test_run_program(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)
        self.assertEqual(1, len(provider.runtime.programs()))

        runtime_program = provider.runtime.program(program_id)
        self.assertIsNotNone(runtime_program)
        try:
            provider.runtime.run(program_id, options=None, inputs={"iterations": 2})
        except Exception:
            self.fail("should pass")


    def test_programs(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        provider.runtime.upload_program("fake-program1", metadata=RUNTIME_PROGRAM_METADATA)
        provider.runtime.upload_program("fake-program2", metadata=RUNTIME_PROGRAM_METADATA)
        programs = provider.runtime.programs()
        self.assertEqual(len(programs), 2)

    def test_pprint_programs(self):
        provider = EmulatorProvider()
        self.assertIsNotNone(provider)
        self.assertIsNotNone(provider.runtime)

        pr_id_1 = provider.runtime.upload_program("fake-program1", metadata=RUNTIME_PROGRAM_METADATA)
        import sys
        import io
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        provider.runtime.pprint_programs()
        output = new_stdout.getvalue()
        sys.stdout = old_stdout
        self.assertTrue(output.startswith( 
        '''==================================================
{}:
  Name: {}'''.format(pr_id_1,pr_id_1)
        ))

    def test_has_service(self):
        provider = EmulatorProvider()
        self.assertTrue(provider.has_service('runtime'))
        self.assertFalse(provider.has_service('fake-service'))

    def test_metadata(self):
        provider = EmulatorProvider()
        
        pr_id = provider.runtime.upload_program("fake-program1", metadata=RUNTIME_PROGRAM_METADATA)
        program = provider.runtime.program(pr_id)
        self.assertEqual(pr_id, program.name)
        self.assertEqual(RUNTIME_PROGRAM_METADATA['description'], program.description)
        self.assertEqual(RUNTIME_PROGRAM_METADATA['max_execution_time'],
                            program.max_execution_time)
        self.assertEqual(RUNTIME_PROGRAM_METADATA["version"], program.version)
        self.assertEqual(RUNTIME_PROGRAM_METADATA['backend_requirements'],
                            program.backend_requirements)
        self.assertEqual([ProgramParameter(**param) for param in
                            RUNTIME_PROGRAM_METADATA['parameters']],
                            program.parameters)
        self.assertEqual([ProgramResult(**ret) for ret in
                            RUNTIME_PROGRAM_METADATA['return_values']],
                            program.return_values)
        self.assertEqual([ProgramResult(**ret) for ret in
                            RUNTIME_PROGRAM_METADATA['interim_results']],
                            program.interim_results)

    def test_circuit_runner(self):
        from . import circuit_runner as cr
        try:
            cr.main()
        except Exception as e:
            self.fail("should pass")