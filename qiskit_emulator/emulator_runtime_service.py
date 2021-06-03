from typing import List, Dict, Optional, Callable, Type, Union, NamedTuple, Any
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.runtime_program import ProgramParameter, ProgramResult
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.providers import ProviderV1 as Provider
import hashlib
import copy
from datetime import datetime 
from pathlib import Path
import os
import json

from . import emulation_executor
from .emulator_runtime_job import EmulatorRuntimeJob

class EmulatorRuntimeService():
    def __init__(self, provider: Provider) -> None:
        self.provider = provider
        self._programs = {}
        self._program_data = {}

    # def pprint_programs(self):
    #     return self._programs

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

        program_metadata = self._merge_metadata(
            initial={},
            metadata=metadata,
            name=name, max_execution_time=max_execution_time, description=description,
            version=version, backend_requirements=backend_requirements,
            parameters=parameters,
            return_values=return_values, interim_results=interim_results)

        program_metadata.pop('name', None)
        
        self._program_data[program_hash] = data
        self._programs[program_hash] = RuntimeProgram(
            program_id = program_hash,
            creation_date= datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            program_name = name,
            **program_metadata
        )
        return program_hash

    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        if program_id in self._programs:
            return self._programs[program_id]
        else:
            return None

    def programs(self, refresh: bool = False) -> List[RuntimeProgram]:
        return self._programs.values()

    def run(
            self,
            program_id: str,
            options: Dict,
            inputs: Dict,
            callback: Optional[Callable] = None,
            result_decoder: Optional[Type[ResultDecoder]] = None
    ) -> EmulatorRuntimeJob:
        if program_id in self._programs:
            program = self._programs[program_id]
            program_data = self._program_data[program_id]
            executor = emulation_executor.EmulationExecutor(program, program_data, options, inputs)
            executor.run()
            job = EmulatorRuntimeJob()
            job.user_messenger = executor._user_messenger
            return job
        else:
            return None
        
    def delete_program(self, program_id: str) -> None:
        print("Do Nothing")

    def job(self, job_id: str) -> EmulatorRuntimeJob:
        print("Do nothing")

    def jobs(self, limit: int = 10, skip: int = 0) -> List[EmulatorRuntimeJob]:
        return []

    def delete_job(self, job_id: str) -> None:
        print("Do Nothing")

    def logout(self) -> None:
        print("Do Nothing")

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

    


