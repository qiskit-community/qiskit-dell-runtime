from qiskit.providers import JobV1
from concurrent import futures
from qiskit.providers import JobStatus, JobError

class EmulatorJob(JobV1):
    _executor = futures.ThreadPoolExecutor(max_workers=1)
    _status = JobStatus.INITIALIZING

    def __init__(self, backend, job_id):
        super().__init__(backend, job_id)
    
    def submit(self):
        # do something
        self._status = JobStatus.RUNNING
        self._executor.submit(print, "do something")
        self._status = JobStatus.DONE

    # @requires_submit
    def result(self, timeout=None):
        return "dummy result"

    # @requires_submit
    def cancel(self):
        # need to actually terminate the thread later
        self._status = JobStatus.CANCELLED

    # @requires_submit
    def status(self):
        return self._status