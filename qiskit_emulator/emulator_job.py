from qiskit.providers import JobV1
from qiskit.providers import JobStatus, JobError
from qiskit import Aer, transpile
import functools

def requires_submit(func):
    """
    Decorator to ensure that a submit has been performed before
    calling the method.
    Args:
        func (callable): test function to be decorated.
    Returns:
        callable: the decorated function.
    """
    @functools.wraps(func)
    def _wrapper(self, *args, **kwargs):
        if self.my_job is None:
            raise JobError("Job not submitted yet!. You have to .submit() first!")
        return func(self, *args, **kwargs)
    return _wrapper

class EmulatorJob(JobV1):
    def __init__(self, backend, job_id, circuit, shots):
        super().__init__(backend, job_id)
        self.circuit = circuit
        self.shots = shots
        self.my_job = None

    @requires_submit
    def result(self, timeout=None):
        return self.my_job.result(timeout=timeout)

    def submit(self):
        backend = Aer.get_backend('aer_simulator')
        self.my_job = backend.run(self.circuit, shots = self.shots)

    @requires_submit
    def cancel(self):
        return self.my_job.cancel()

    @requires_submit
    def status(self):
        return self.my_job.status()