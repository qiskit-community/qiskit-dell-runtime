from qiskit.providers import JobV1
from qiskit.providers import JobStatus, JobError
from qiskit import Aer, transpile

class EmulatorJob(JobV1):
    _status = JobStatus.INITIALIZING

    def __init__(self, backend, job_id, circuit=None):
        super().__init__(backend, job_id)
        self.circuit = circuit
        self.my_job = None

    def result(self, timeout=None):
        if self.my_job is not None:
            return self.my_job.result(timeout=timeout)

    def submit(self):
        # do something
        print('submitting job')
        self._status = JobStatus.QUEUED
        self.run_circuit() 

    def run_circuit(self):
        self._status = JobStatus.RUNNING
        simulator = Aer.get_backend('aer_simulator')
        circ = transpile(self.circuit, simulator)
        self.my_job = simulator.run(circ)

    # @requires_submit
    def cancel(self):
        if self.my_job is not None:
            return self.my_job.cancel()

    # @requires_submit
    def status(self):
        if self.my_job is not None:
            return self.my_job.status()
        else:
            return self._status