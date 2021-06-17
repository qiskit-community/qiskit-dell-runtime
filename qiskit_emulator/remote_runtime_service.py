from typing import List, Dict, Optional, Callable, Type, Union, NamedTuple, Any
from urllib.parse import urljoin
import requests
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.runtime_program import ProgramParameter, ProgramResult
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.providers import ProviderV1 as Provider
import logging
import copy
import json
from .emulator_runtime_job import EmulatorRuntimeJob

logger = logging.getLogger(__name__)

class RemoteRuntimeService():
    def __init__(self, provider: Provider, host: str) -> None:
        self.provider = provider
        self.host = host
        status_response = self._get("/status")
        if not (status_response[0] == 200):
            raise Exception("Wrong status code from host: {}".format(self.host))
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
        
    def programs(self, refresh: bool = False):
        if refresh or (self._programs == {}):
            res = self._get('/program')
            if res[0] != 200:
                logger.error(f'Cannot fetch programs: {res[0]}')
            else:
                proglist = json.loads(res[2])
                self._programs = {}
                for prog in proglist:
                    program_metadata = json.loads(prog['program_metadata'])
                    self._programs[prog['program_id']] = RuntimeProgram(program_name=prog['name'], 
                                                        program_id=prog['program_id'], 
                                                        description=program_metadata['description'], 
                                                        max_execution_time=(int(program_metadata['max_execution_time']) if 'max_execution_time' in program_metadata else 0),
                                                        parameters=(program_metadata['parameters'] if 'parameters' in program_metadata else None)  ,
                                                        return_values=(program_metadata['return_values'] if 'return_values' in program_metadata else None),
                                                        interim_results=(program_metadata['interim_results'] if 'interim_results' in program_metadata else None),
                                                        version=(program_metadata['version'] if 'version' in program_metadata else "0"),
                                                        backend_requirements=(program_metadata['backend_requirements'] if 'backend_requirements' in program_metadata else None),
                                                        creation_date=(program_metadata['creation_date'] if 'creation_date' in program_metadata else ""))

        return self._programs


    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        if (not refresh) and program_id in self._programs:
            return self._programs[program_id]
        else:
            self.programs(refresh=True)
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
            program_id: Optional[str] = None,
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
        if program_id == None:
            program_id = hex(hash((data, name, version)))[-16:]
            if name is None:
                name = program_id

        program_metadata = self._merge_metadata(
            initial={},
            metadata=metadata,
            name=name, max_execution_time=max_execution_time, description=description,
            version=version, backend_requirements=backend_requirements,
            parameters=parameters,
            return_values=return_values, interim_results=interim_results)
        program_metadata.pop('name', None)

        req_body = {
            'program_id': program_id,
            'data': data,
            'name': name,
            'program_metadata': program_metadata
        }

        res = self._post('/program', req_body)
        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
        else:
            logger.debug(f"Received program_id: {res[2]}")
            return res[2]

    def delete_program(
        self,
        program_id: str,
    ) -> str:
        res = self._get(f'/program/{program_id}/delete')
        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
            return False
        else:
            logger.debug(f"Deleted {program_id} successfully")
            return True
    
    def run(
            self,
            program_id: str,
            options: Dict,
            inputs: Dict,
            callback: Optional[Callable] = None,
            result_decoder: Optional[Type[ResultDecoder]] = None
    ) -> EmulatorRuntimeJob:
        serialized_inputs = json.dumps(inputs, cls=RuntimeEncoder)
        res = self._post('/program/{}/job'.format(program_id), serialized_inputs)
        if (res[0] != 200):
            raise Exception('Something went bad')
        job = EmulatorRuntimeJob(res[2], self.host)
        return job

    def update_program(
            self,
            program_id: str,

            # We include data as a field even though we don't get it
            # back from program() as part of RuntimeProgram.
            # We are assuming it gets updated.

            data: Optional[Union[bytes, str]] = None,
            metadata: Optional[Union[Dict, str]] = None,
            name: Optional[str] = None,
            max_execution_time: Optional[int] = None,
            description: Optional[str] = None,
            version: Optional[float] = None,
            backend_requirements: Optional[str] = None,
            parameters: Optional[List[ProgramParameter]] = None,
            return_values: Optional[List[ProgramResult]] = None,
            interim_results: Optional[List[ProgramResult]] = None
    ):
        program_metadata = self._merge_metadata(
            initial={},
            metadata=metadata,
            name=name, max_execution_time=max_execution_time, description=description,
            version=version, backend_requirements=backend_requirements,
            parameters=parameters,
            return_values=return_values, interim_results=interim_results)
        program_metadata.pop('name', None)

        req_body = {
            'program_id': program_id,
            'data': data,
            'name': name,
            'program_metadata': program_metadata
        }

        res = self._post(f'/program/{program_id}/update', req_body)
        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
            return False
        else:
            logger.debug(f"Successfully updated program {program_id}")
            return True

    # copied from IBM runtime service
    def _merge_metadata(
            self,
            initial: Dict,
            metadata: Optional[Union[Dict, str]] = None,
            **kwargs: Any
    ) -> Dict:
        """Merge multiple copies of metadata.
        Args:
            initial: The initial metadata. This may be mutated.
            metadata: Name of the program metadata file or metadata dictionary.
            **kwargs: Additional metadata fields to overwrite.
        Returns:
            Merged metadata.
        """
        upd_metadata = {}
        if metadata is not None:
            if isinstance(metadata, str):
                with open(metadata, 'r') as file:
                    upd_metadata = json.load(file)
            else:
                upd_metadata = copy.deepcopy(metadata)

        self._tuple_to_dict(initial)
        initial.update(upd_metadata)

        self._tuple_to_dict(kwargs)
        for key, val in kwargs.items():
            if val is not None:
                initial[key] = val

        # TODO validate metadata format
        metadata_keys = ['name', 'max_execution_time', 'description', 'version',
                         'backend_requirements', 'parameters', 'return_values',
                         'interim_results']
        return {key: val for key, val in initial.items() if key in metadata_keys}

    def _tuple_to_dict(self, metadata: Dict) -> None:
        """Convert fields in metadata from named tuples to dictionaries.
        Args:
            metadata: Metadata to be converted.
        """
        for key in ['parameters', 'return_values', 'interim_results']:
            doc_list = metadata.pop(key, None)
            if not doc_list or isinstance(doc_list[0], dict):
                continue
            metadata[key] = [dict(elem._asdict()) for elem in doc_list]

