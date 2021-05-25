from qiskit.providers import JobV1
from concurrent import futures
from qiskit.providers import JobStatus, JobError
from qiskit import Aer, transpile

def run_circuit(job):
    job._status = JobStatus.RUNNING
    simulator = Aer.get_backend('aer_simulator')
    circ = transpile(job.circuit, simulator)
    result = simulator.run(circ).result()
    job.result = result
    job._status = JobStatus.DONE

class EmulatorJob(JobV1):
    _executor = futures.ThreadPoolExecutor(max_workers=1)
    _status = JobStatus.INITIALIZING

    def __init__(self, backend, job_id, circuit=None):
        super().__init__(backend, job_id)
        self.circuit = circuit

    def submit(self):
        # do something
        self._status = JobStatus.QUEUED
        self._executor.submit(run_circuit, self) 

    # @requires_submit
    def result(self, timeout=None):
        return self.result

    # @requires_submit
    def cancel(self):
        # need to actually terminate the thread later
        self._status = JobStatus.CANCELLED

    # @requires_submit
    def status(self):
        return self._status