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
import threading
from datetime import datetime
import json

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

        self._imsgs = []
        self._msgRead = 0
        self._poller = threading.Thread(target=self.poll_for_results)
        self._finalResults = None
        self._kill = False
        self._poller.start()

# Ben 6/17/21: implemented thread to poll for messages until there's a final
#              result. Once there's a final result exit thread.

# Does not yet work with multiple messages - need to adjust orchestrator 
# and db_service in order to accomodate getting unread messages (or all)
# perhaps easier to just get all, send back to ERJ, and sort them out there?



    def __del__(self):
        self._kill = True
        try:            
            self._poller.join()
        except:
            logger.debug("poller thread joined")


    def poll_for_results(self):
        dcd = self.result_decoder
        lastTimestamp = None

        while not self._finalResults:     
            if self._kill:
                break

            time.sleep(3)

            url = self.getURL('/job/'+ self.job_id +'/results')
            if lastTimestamp:
                url = self.getURL('/job/'+ self.job_id +'/results/' + str(lastTimestamp))
            
            response = requests.get(url)
            if response.status_code == 204:
                logger.debug('result: status 204, no new messages.')
                continue
            # response.raise_for_status()
            res_json = json.loads(response.text)
            logger.debug(f'got: {res_json}')
            messages = res_json["messages"]

            logger.debug(f'result: got {messages}')

            for msg in messages:
                if not lastTimestamp:
                    lastTimestamp = datetime.fromisoformat(msg['timestamp'])
                else:
                    msgTime = datetime.fromisoformat(msg['timestamp'])
                    if lastTimestamp < msgTime:
                        lastTimestamp = msgTime

                msg_data = json.loads(msg['data'])
                if msg_data['final']:
                    logger.debug('result: got final result.')
                    self._finalResults = msg_data['message']
                else:
                    self._imsgs.append(msg_data['message'])
        return


    def getURL(self, path):
        url = urljoin(self.host, path)
        logger.debug(f"{url}")
        return url

    # def result(
    #         self,
    #         timeout: Optional[float] = None,
    #         wait: float = 5,
    #         decoder: Optional[Type[ResultDecoder]] = None
    # ) -> Any:
    #     stime = time.time()
    #     isFinal = False
    #     finalMessage = None
    #     dcd = decoder or self.result_decoder
    #     while not isFinal:
    #         elapsed_time = time.time() - stime
    #         if timeout is not None and elapsed_time >= timeout:
    #             raise 'Timeout while waiting for job {}.'.format(self.job_id)
    #         time.sleep(wait)
    #         response = requests.get(self.getURL('/job/'+ self.job_id +'/results'))
    #         if response.status_code == 204:
    #             logger.debug('result: status 204, job not done.')
    #             continue
    #         # response.raise_for_status()
    #         result = dcd.decode(response.text)

    #         if result['final']:
    #             isFinal = True
    #             finalMessage = result['message']
        
    #     return finalMessage

    def result(self, 
               timeout: Optional[float] = None):
        if timeout is not None:
            stime = time.time()
            while not self._finalResults:
                elapsed_time = time.time() - stime
                if elapsed_time >= timeout:
                    raise 'Timeout while waiting for job {}.'.format(self.job_id)
                time.sleep(3)
        
        return self._finalResults

    def get_unread_messages(self):
        if len(self._imsgs) == self._msgRead:
            return []
        else:
            strt = self._msgRead
            self._msgRead = len(self._imsgs)
            return self._imsgs[strt:]
    
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

    # def stream_results(
    #         self,
    #         callback: Callable,
    #         decoder: Optional[Type[ResultDecoder]] = None
    # ) -> None:
    #     dcd = decoder or self.result_decoder
    #     isFinal = False
    #     while not isFinal:
    #         response = requests.get(self.getURL('/jobs/'+ self.job_id +'/results'))
    #         response.raise_for_status()
    #         results = dcd.decode(response.text)
    #         for result in results:
    #             callback(result['message'])
    #             isFinal = result['final']
                    

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