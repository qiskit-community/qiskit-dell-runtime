"""Qiskit emulator runtime job."""

from typing import Any, Optional, Callable, Dict, Type
import time
import logging
import asyncio
from concurrent import futures
import traceback
import queue
from datetime import datetime
from qiskit.providers.ibmq.runtime.program.result_decoder import ResultDecoder
from urllib.parse import urljoin
import requests

logger = logging.getLogger(__name__)
 

class EmulatorRuntimeJob:
    """Representation of a runtime program execution.
    A new ``EmulatorRuntimeJob`` instance is returned when you call
        job = provider.runtime.run(...)
    """

    def __init__(
            self,
            job_id,
            host,
            result_decoder: Type[ResultDecoder] = ResultDecoder
    ) -> None:
        """RuntimeJob constructor.
        Args:
        """
        self.job_id = job_id
        self.host = host
        self.result_decoder = result_decoder

    def getURL(self, path):
        url = urljoin(self.host, path)
        logger.debug(f"{url}")
        return url

    def result(
            self,
            timeout: Optional[float] = None,
            wait: float = 5,
            decoder: Optional[Type[ResultDecoder]] = None
    ) -> Any:
        stime = time.time()
        isFinal = False
        finalMessage = None
        dcd = decoder or self.result_decoder
        while not isFinal:
            elapsed_time = time.time() - stime
            if timeout is not None and elapsed_time >= timeout:
                raise 'Timeout while waiting for job {}.'.format(self.job_id)
            time.sleep(wait)
            response = requests.get(self.getURL('/job/'+ self.job_id +'/results'))
            if response.status_code == 204:
                logger.debug('result: status 204, job not done.')
                continue
            # response.raise_for_status()
            result = dcd.decode(response.text)

            if result['final']:
                isFinal = True
                finalMessage = result['message']
        
        return finalMessage

    
    
    def cancel(self) -> None:
        """Cancel the job.
        """
      
    #def status(self) -> JobStatus:
    #    """Return the status of the job.
    #    Returns:
    #        Status of this job.
    #    Raises:
    #    """

    def wait_for_final_state(
            self,
    ) -> None:
        """Poll the job status until it progresses to a final state such as ``DONE`` or ``ERROR``.
        Args:
        Raises:
        """

    def stream_results(
            self,
            callback: Callable,
            decoder: Optional[Type[ResultDecoder]] = None
    ) -> None:
        dcd = decoder or self.result_decoder
        isFinal = False
        while not isFinal:
            response = requests.get(self.getURL('/jobs/'+ self.job_id +'/results'))
            response.raise_for_status()
            results = dcd.decode(response.text)
            for result in results:
                callback(result['message'])
                isFinal = result['final']
                    

    def cancel_result_streaming(self) -> None:
        """Cancel result streaming."""

    def _start_websocket_client(
            self,
    ) -> None:
        """Start websocket client to stream results.
        Args:
        """

    def _stream_results(
            self,
    ) -> None:
        """Stream interim results.
        Args:
        """

    def _empty_result_queue(self, result_queue: queue.Queue) -> None:
        """Empty the result queue.
        Args:
        """

    def job_id(self) -> str:
        """Return a unique ID identifying the job.
        Returns:
            Job ID.
        """
        return self._job_id

    #def backend(self) -> Backend:
    #    """Return the backend where this job was executed.
    #    Returns:
    #        Backend used for the job.
    #    """
    #    return self._backend

    @property
    def inputs(self) -> Dict:
        """Job input parameters.
        Returns:
            Input parameters used in this job.
        """
        return self._params

    @property
    def program_id(self) -> str:
        """Program ID.
        Returns:
            ID of the program this job is for.
        """
        return self._program_id

    @property
    def creation_date(self) -> Optional[datetime]:
        """Job creation date in local time.
        Returns:
            The job creation date as a datetime object, in local time, or
            ``None`` if creation date is not available.
        """
    @property
    def user_messenger(self):
        return self._user_messenger
      
    @user_messenger.setter
    def user_messenger(self, messenger):
        self._user_messenger = messenger