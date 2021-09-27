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

from dell_runtime.emulation_executor import EmulationExecutor
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
import socket

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
            session: Optional[Type[requests.Session]] = None,
            executor: Optional[Type[EmulationExecutor]] = None,
            result_decoder: Type[ResultDecoder] = ResultDecoder,
            callback: Optional[Callable] = None
    ) -> None:
        """RuntimeJob constructor.
        Args:
        """
        self.job_id = job_id

        self.host = host
        self._sock = None
        self.local_port = None

        self.executor = executor
        self.session = session

        self._status = None
        self._msgRead = 0

        self._imsgs = []
        self._finalResults = None
        self._kill = False
        
        if not self.host:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.bind(('localhost', 0))
            self.local_port = self._sock.getsockname()[1]
            logger.debug(self.local_port)
            self._poller = threading.Thread(target=self.local_poll_for_results, args=(callback,))
        else:
            self._poller = threading.Thread(target=self.remote_poll_for_results,args=(callback,))

        self.result_decoder = result_decoder

        self._poller.start()

        if self.executor:
            self.executor._local_port = self.local_port
            self.executor.run()

    def __del__(self):
        self._kill = True
        try:            
            self._poller.join()
        except:
            logger.debug("poller thread joined")
        
        # self.executor.__del__()

    def job_completed(self):
        self.status()
        return (self._status == "Failed" or self._status == "Completed" or self._status == "Canceled")

    def local_poll_for_results(self,callback):
        logging.debug(f"starting to listen to port {self.local_port}")
        self._sock.listen(1)
        self._sock.settimeout(3)
        try:
            conn, addr = self._sock.accept()
            logging.debug(f"accepted client connection from {addr}")
            with conn:
                while self._finalResults == None and not self._kill and not self.job_completed():
                    data = conn.recv(16384)

                    if not data:
                        break
                    else:
                        data_str = data.decode('utf-8')
                        msgs = data_str.split('\u0004')[:-1]
                        for msg in msgs:
                            data_obj = json.loads(msg, cls=self.result_decoder)
                            # print(f"MESSENGER RECEIVED: {data_obj}")
                            message = data_obj["message"]
                            
                            if data_obj['final']:
                                logger.debug('result: got final result.')
                                self._finalResults = message
                            else:
                                self._imsgs.append(message)
                                if callback is not None:
                                    callback(message)
                self._sock.close()
                logger.debug("local thread: exiting")
                return
        except socket.timeout as e:
            logger.debug(e)


    def remote_poll_for_results(self, callback):
        dcd = self.result_decoder
        lastTimestamp = None
        stay_alive = True
        final_loop = False

        while stay_alive:     
            time.sleep(3)

            url = self.getURL('/job/'+ self.job_id +'/results')
            if lastTimestamp:
                url = self.getURL('/job/'+ self.job_id +'/results/' + str(lastTimestamp))
            
            response = self.session.get(url)
            if response.status_code == 204:
                logger.debug('result: status 204, no new messages.')
                continue
            response.raise_for_status()
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
                    logger.debug("appended message to queue")
                    if callback is not None:
                        logger.debug('Callback is here')
                        callback(msg_data['message'])
            if final_loop:
                stay_alive = False
                continue
            final_loop = not (self._finalResults == None and not self._kill and not self.job_completed())
            # logger.debug(f"final: {final_loop}")
            # logger.debug(f"results: {self._finalResults}")
            # logger.debug(f"kill: {self._kill}")
            # logger.debug(f"completed: {self.job_completed()}")

        return


    def getURL(self, path):
        url = urljoin(self.host, path)
        logger.debug(f"{url}")
        return url


    def result(self, 
               timeout: Optional[float] = None):
        if timeout is not None:
            stime = time.time()
            while self._finalResults == None:
                elapsed_time = time.time() - stime
                if elapsed_time >= timeout:
                    self._kill = True
                    raise Exception('Timeout while waiting for job {}.'.format(self.job_id))
                time.sleep(1)
        
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
        self._kill = True
        if self.executor:
            self.executor.cancel()
            return True
        
        url = self.getURL('/job/' + self.job_id + '/cancel')
        response = self.session.get(url)
        response.raise_for_status()
        
        if response.status_code == 200:
            return True
        elif response.status_code == 204:
            return False
      
    def status(self):
        """Return the status of the job.
        Returns:
            Status of this job.
        Raises:
        """
        if self.executor:
            return self.executor.get_status()

        url = self.getURL('/job/' + self.job_id + '/status')
        response = self.session.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            self._status = response.text
            return self._status
        elif response.status_code == 204:
            return None

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