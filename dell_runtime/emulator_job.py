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