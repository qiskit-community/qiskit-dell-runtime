from typing import List, Dict, Optional, Callable, Type, Union, NamedTuple, Any
from urllib.parse import urljoin
import requests
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.runtime_program import ProgramParameter, ProgramResult
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.providers import ProviderV1 as Provider
import logging

logger = logging.getLogger(__name__)

class RemoteRuntimeService():
    def __init__(self, provider: Provider, host: str) -> None:
        self.provider = provider
        self.host = host
        self._programs = {}

    # def pprint_programs(self):
    #     return self._programs

    def _post(self, path, data):
        url = urljoin(self.host, path)
        logger.debug(f"POST {url}: {data}")
        req = requests.post(url, json=data)

        res = (req.status_code, req.reason, req.text)
        logger.debug(f"POST {url} RESPONSE: {res}")
        return res
    
    def _get(self, path):
        url = urljoin(self.host, path)
        logger.debug(f"GET {url}")
        req = requests.get(url)
        res = (req.status_code, req.reason, req.text)
        logger.debug(f"GET {url} RESPONSE: {res}")
        return res
        
    def programs(self, refresh: bool = False) -> List[RuntimeProgram]:
        res = self._get('/program')
        if res[0] != 200:
            logger.error(f'Cannot fetch programs: {res[0]}')
        else:
            return res[2]

    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        if program_id in self._programs:
            return self._programs[program_id]
        else:
            return None

    # copied from IBMQ Provider
    def pprint_programs(self, refresh: bool = False) -> None:
        """Pretty print information about available runtime programs.

        Args:
            refresh: If ``True``, re-query the server for the programs. Otherwise
                return the cached value.
        """
        programs = self.programs(refresh)
        for prog in programs:
            print("="*50)
            print(str(prog))

    def upload_program(
            self,
            data: Union[bytes, str],
            metadata: Optional[Union[Dict, str]] = None,
            name: Optional[str] = None,
            max_execution_time: Optional[int] = None,
            description: Optional[str] = None,
            version: Optional[float] = None,
            backend_requirements: Optional[str] = None,
            parameters: Optional[List[ProgramParameter]] = None,
            return_values: Optional[List[ProgramResult]] = None,
            interim_results: Optional[List[ProgramResult]] = None
    ) -> str:
        # careful of hash collision
        program_hash = hex(hash((data, name, version)))[-16:]
        if name is None:
            name = program_hash

        req_body = {
            'program_id': program_hash,
            'data': data,
            'name': name,
            'description': description
        }

        res = self._post('/program', req_body)
        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
        else:
            return res[2]


